import nextcord
from nextcord.ext import commands
import http.client
import json

class WeatherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @nextcord.slash_command(name="weather")
    async def get_weather(self, interaction: nextcord.Interaction, city: str):
        await interaction.response.defer()
        weather_data, error = self.get_weather_data(city)
        if error:
            await interaction.followup.send(error)
        elif weather_data is None:
            await interaction.followup.send("City not found!")
        else:
            weather_info = self.display_weather(weather_data)
            
            embed = nextcord.Embed(
                title=f"Weather in {weather_data['city']}",
                description=weather_info,
                color=0x1E90FF  # DodgerBlue color
            )
            embed.add_field(name="Temperature", value=f"{weather_data['current_weather']['temperature']:.2f}°C")
            embed.add_field(name="Wind Speed", value=f"{weather_data['current_weather']['windspeed']:.2f} km/h")
            embed.add_field(name="Condition", value=self.interpret_weather_code(weather_data['current_weather']['weathercode']))
            embed.set_footer(text="Weather data provided by Open-Meteo")

            await interaction.followup.send(embed=embed)

    def get_weather_data(self, city):
        try:
            # Geocoding API request
            conn = http.client.HTTPSConnection("geocoding-api.open-meteo.com")
            conn.request("GET", f"/v1/search?name={city}")
            response = conn.getresponse()
            geocoding_data = json.loads(response.read())
            conn.close()

            if 'results' not in geocoding_data or len(geocoding_data['results']) == 0:
                return None, "City not found!"

            latitude = geocoding_data['results'][0]['latitude']
            longitude = geocoding_data['results'][0]['longitude']
            city_name = geocoding_data['results'][0]['name']

            # Weather API request
            conn = http.client.HTTPSConnection("api.open-meteo.com")
            conn.request("GET", f"/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true")
            response = conn.getresponse()
            weather_data = json.loads(response.read())
            conn.close()

            weather_data['city'] = city_name  # Add city name to the weather data

            return weather_data, None
        except Exception as e:
            return None, str(e)

    def interpret_weather_code(self, code):
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Drizzle: Light",
            53: "Drizzle: Moderate",
            55: "Drizzle: Dense intensity",
            56: "Freezing Drizzle: Light",
            57: "Freezing Drizzle: Dense intensity",
            61: "Rain: Slight",
            63: "Rain: Moderate",
            65: "Rain: Heavy intensity",
            66: "Freezing Rain: Light",
            67: "Freezing Rain: Heavy intensity",
            71: "Snow fall: Slight",
            73: "Snow fall: Moderate",
            75: "Snow fall: Heavy intensity",
            77: "Snow grains",
            80: "Rain showers: Slight",
            81: "Rain showers: Moderate",
            82: "Rain showers: Violent",
            85: "Snow showers slight",
            86: "Snow showers heavy",
            95: "Thunderstorm: Slight or moderate",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, "Unknown weather code")

    def display_weather(self, data):
        city = data['city']
        weather_code = data['current_weather']['weathercode']
        weather = self.interpret_weather_code(weather_code)
        temp = data['current_weather']['temperature']
        wind_speed = data['current_weather']['windspeed']

        weather_info = (
            f"{city}\n"
            f"Weather: {weather}\n"
            f"Temperature: {temp:.2f}°C\n"
            f"Wind Speed: {wind_speed:.2f} km/h\n"
        )
        return weather_info

def setup(bot):
    bot.add_cog(WeatherCog(bot))
