class SoilMoistureSensor():
    def get_moisture_coefficient(self, v_moisture_sensor):
        """
        args:
            v_moisture_sensor: output voltage from the capacitive soild moisture sensor
        returns:
            wet_coefficeint: measure how wet the soil is from 0 to 1 where 1 is the wettest
        """
        VOUT_DRY_AIR = 2.845
        VOUT_WATER_SUBMERGED = 1.39
        VOUT_RANGE = VOUT_DRY_AIR - VOUT_WATER_SUBMERGED
        wet_coefficient = 1 - ((v_moisture_sensor - 1.39)/VOUT_RANGE)
        return wet_coefficient
    
    def is_soil_wet(self, v_moisture_sensor):
        wet_coefficient = self.get_moisture_coefficient(v_moisture_sensor)
        if wet_coefficient >= 0.237:
            return True
        else:
            return False
    
    def get_relative_moisture_coefficient(self, v_moisture_sensor, prev_max_coeff):
        """
        args:
            curr_coeff: current soil moisture coefficient
        returns:
            prev_max_coeff: maximum ground wetness in the previous wet event
        """
        curr_coeff = self.get_moisture_coefficient(v_moisture_sensor)
        relative_coeff = 1 - (prev_max_coeff - curr_coeff)
        return relative_coeff

class RainLevelSensor():
    def get_rain_level_coefficient(self, v_rain_sense):
        VOUT_DRY = 4.09
        VOUT_WET = 3.8
        VOUT_DRY_RANGE = VOUT_DRY - VOUT_WET
        wet_coefficient = (VOUT_DRY - v_rain_sense)/VOUT_DRY_RANGE
        return wet_coefficient
    
    def is_it_raining(self, v_rain_sense):        
        if self.get_rain_level_coefficient(v_rain_sense) >= 1:
            return True
        else:
            return False

class TemperatureSensor():
    def get_relative_tepmerature_coefficient(self, curr_avg_temp, prev_avg_temp):
        MAX_TEMPERATURE = 45
        MIN_TEMPERATURE = 0
        TEMPERATURE_RANGE = MAX_TEMPERATURE - MIN_TEMPERATURE

        temperature_cefficient = 1 - (curr_avg_temp - prev_avg_temp)/TEMPERATURE_RANGE
        return temperature_cefficient
