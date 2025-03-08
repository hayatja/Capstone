from db_tacker import *
from sensor_coefficients import *

from datetime import datetime
def time_difference_from_now(target_time_str):
    # Parse the target time string
    target_time = datetime.strptime(target_time_str, "%Y-%m-%d %H:%M:%S")
    
    # Get the current time
    current_time = datetime.now()
    
    # Calculate the time difference in hours
    time_difference = (target_time - current_time).total_seconds() / 3600
    
    return time_difference

def estimate_drying_time(data_tracker, soil_moisture_sens, temperature_sensor, sensor_out_dict, current_wet_event):
    history_entry = data_tracker.get_last_drying_time()
    prev_dry_time = history_entry['time_to_dry']
    prev_initial_moisture = history_entry['initial_soil_moisture']
    prev_avg_temp = history_entry['average_temperature']
    
    relative_soil_moisture_coeff = soil_moisture_sens.get_relative_moisture_coefficient(sensor_out_dict['soil_moisture'], prev_initial_moisture)
    
    curr_avg_temp = current_wet_event['average_temperature']
    relative_temerature_coeff = temperature_sensor.get_relative_tepmerature_coefficient(curr_avg_temp, prev_avg_temp)
    
    time_estimate = prev_dry_time*relative_soil_moisture_coeff*relative_temerature_coeff
    return time_estimate
            
def main():
    # initialize data tracking and processing objects
    data_tracker = DataTracker()
    
    soil_moisture_sens = SoilMoistureSensor()
    rain_level_sens = RainLevelSensor()
    temperature_sensor = TemperatureSensor()
    
    # get last data entry
    sensor_out_dict = data_tracker.get_last_data_entry()
    wet_event = data_tracker.is_there_ongoing_wet_event()
    rain = rain_level_sens.is_it_raining(sensor_out_dict['rain_level'])
    soil_is_wet = soil_moisture_sens.is_soil_wet(sensor_out_dict['soil_moisture'])
    soild_moisture_coeff = soil_moisture_sens.get_moisture_coefficient(sensor_out_dict['soil_moisture'])
    
    if rain: 
    # if theres an ongoing wet event delete it to update with new rain data
        if wet_event:
            data_tracker.reset_ongoing_wet_event()
        else:
            # maybe here update
            print("It's still raining, can't etimate drying time")
        
        exit()
    
    # if no rain, soil is wet
    if soil_is_wet:
        print("soil is wet\n")
        if wet_event:
            print("there's a wet event\n")
            # update wet event
            current_wet_event = data_tracker.get_wet_event_values()
            update_number = current_wet_event['number_of_updates']
            avg_temp = current_wet_event['average_temperature']
            avg_temp = ((avg_temp * update_number) + sensor_out_dict['temperature'])/(update_number + 1)
            update_number = update_number + 1
            
            # estimate remaining drying time
            time_estimate = estimate_drying_time(data_tracker, soil_moisture_sens, temperature_sensor, sensor_out_dict, current_wet_event)
            print(f"Time estimate until Soil is dry: {time_estimate}")
            update_data = {"average_temperature": avg_temp, "number_of_updates": update_number, "time_estimate": time_estimate}
            data_tracker.update_wet_event(update_data)

        elif not wet_event:
            print("there isn't a wet event creating a wet event\n")
            # create wet event
            wet_event_data = {"average_temperature": sensor_out_dict['temperature'], "number_of_updates": 0, 
                              'initial_soil_moisture': soild_moisture_coeff, 'time_estimate': 25}
            data_tracker.create_wet_event(wet_event_data)

    elif not soil_is_wet:
        if wet_event:
            print("soil is no longer wet, recording drying time to history\n")
            # save this wet event to history
            current_wet_event = data_tracker.get_wet_event_values()
            avg_temp = current_wet_event['average_temperature']
            initial_time = current_wet_event['initial_time']
            initial_soil_moisture = current_wet_event['initial_soil_moisture']
    
            hours_difference = time_difference_from_now(str(initial_time)) 
            
            history_data = {'initial_time': initial_time, 'average_temperature': avg_temp, 
                'initial_soil_moisture': initial_soil_moisture, 'time_to_dry': hours_difference}

            data_tracker.save_event_to_history(history_data)
            
            # delete ongoing wet event
            data_tracker.reset_ongoing_wet_event() 
                        
        elif not wet_event:
            print("sun on sun\n")
            # there is nothing to do, pass


if __name__ == "__main__":
    main()