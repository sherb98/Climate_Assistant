import pandas as pd
from pythermalcomfort.models import pmv
import matplotlib.pyplot as plt
import os
    
def create_bar_chart2(data, bar_names, ylabel, color, title, ref_value, tolerance_PMV, filename_base):
    plt.rcParams.update({'font.size': 3})
    plt.figure(figsize=(4, 1.5))
    bars = plt.bar(bar_names, data, color=color)

    AC_needed = True
    start_box = None
    compliance_labels = []
    for i, (bar, value) in enumerate(zip(bars, data)):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval), va='bottom', ha='center')
        
        if ref_value is not None and yval != ref_value:
            pct_change = ((yval - ref_value) / ref_value) * 100
            plt.text(bar.get_x() + bar.get_width()/2, yval / 2, f"{pct_change:+.1f}%", va='center', ha='center', color='white')

        # Identify the first bar that exceeds the tolerance and calculate the middle point
        if value < tolerance_PMV and start_box is None:
            AC_needed = False
            if i > 0:
                prev_bar = bars[i-1]
                start_box = (bar.get_x() + prev_bar.get_x() + prev_bar.get_width()) / 2
            else:
                start_box = bar.get_x()

        # Mark the bars that are in compliance
        if value <= tolerance_PMV:
            compliance_labels.append((bar.get_x() + bar.get_width() / 2, -0.11 * max(data)))

    # Draw the green background
    if start_box is not None:
        plt.axvspan(start_box, bars[-1].get_x() + bars[-1].get_width(), color='green', alpha=0.3)

    plt.ylabel(ylabel, fontsize=3)
    plt.xticks(ticks=range(len(bar_names)), labels=bar_names, rotation=0, fontsize=3)
    plt.title(title)

    # Add "Compliance" text in green under the bars that meet the PMV threshold
    for x, y in compliance_labels:
        plt.text(x, y, "Compliance", ha='center', va='top', color='green', fontsize=3)

    plt.tight_layout()
    
    filename=os.path.join('static',filename_base+'_'+str(AC_needed)+'.png')
    # Save the plot as a PNG file
    plt.savefig(filename, bbox_inches='tight', dpi=300)
    pngname = os.path.basename(filename)
    return pngname
    


def load_and_process_data(file_paths,ambient_prefix):
    #columns to extract from the output file
    columns = [
        "ZONE_0:Zone Mean Radiant Temperature [C](Hourly)",
        "ZONE_0:Zone Mean Air Temperature [C](Hourly)",
        "ZONE_0:Zone Mean Air Humidity Ratio [kgWater/kgDryAir](Hourly)",
        "ZONE_0:Zone Air Relative Humidity [%](Hourly)",
        
    ]

    columns_weather = [
        "Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)",
        "Environment:Site Outdoor Air Humidity Ratio [kgWater/kgDryAir](Hourly)",
        "Environment:Site Outdoor Air Relative Humidity [%](Hourly)",
        "PEOPLE ZONE_0:Zone Thermal Comfort ASHRAE 55 Adaptive Model Running Average Outdoor Air Temperature [C](Hourly)"  
    ]
    
    nested_dict = {}
    df_weather = pd.read_csv(file_paths[0], usecols=columns_weather)
    df_weather["Duplicate_Column"] = df_weather['Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)']
    df_weather.rename(columns={
        'Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)': 'Indoor_Radiant_Temp_C',
        'Duplicate_Column': 'Indoor_Air_Temp_C',
        'Environment:Site Outdoor Air Relative Humidity [%](Hourly)': 'Indoor_Rel_Hum',
        "PEOPLE ZONE_0:Zone Thermal Comfort ASHRAE 55 Adaptive Model Running Average Outdoor Air Temperature [C](Hourly)": "RunnAvg_Out_Air_Temp",
        "Environment:Site Outdoor Air Humidity Ratio [kgWater/kgDryAir](Hourly)": 'Indoor_Humidity_Ratio'
    }, inplace=True)
    nested_dict[ambient_prefix] = df_weather

    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path, usecols=columns)
            df.rename(columns={
                'ZONE_0:Zone Mean Radiant Temperature [C](Hourly)': 'Indoor_Radiant_Temp_C',
                'ZONE_0:Zone Mean Air Temperature [C](Hourly)': 'Indoor_Air_Temp_C',
                'ZONE_0:Zone Mean Air Humidity Ratio [kgWater/kgDryAir](Hourly)': 'Indoor_Humidity_Ratio',
                'ZONE_0:Zone Air Relative Humidity [%](Hourly)': 'Indoor_Rel_Hum'
            }, inplace=True)
            parts=file_path.split("_")            
            #create collumn name
            parts.pop(0)  
            parts[-1] = parts[-1].replace("out.csv", "")  
            coll_name = "_".join(parts)
            
            nested_dict[coll_name] = df
        except Exception as e:
            nested_dict[coll_name] = f"Error reading file {file_path}: {e}"

    return nested_dict



def calculate_pmv(nested_dict, vr, met, clo, PMV_too_hot):
    for df in nested_dict.values():
        df['PMV'] = df.apply(lambda row: pmv(tdb=row['Indoor_Air_Temp_C'], 
                                             tr=row['Indoor_Radiant_Temp_C'], 
                                             vr=vr, 
                                             rh=row['Indoor_Rel_Hum'],
                                             met=met, 
                                             clo=clo, 
                                             units='SI',
                                             limit_inputs=False), axis=1)
        df['too_hot'] = df['PMV'].apply(lambda x: 1 if x > PMV_too_hot else 0)
        
    return nested_dict
    


def create_bar_chart(data, bar_names, ylabel, color, title, ref_value=None):
    plt.figure(figsize=(12, 8))
    bars = plt.bar(bar_names, data, color=color)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval), va='bottom', ha='center')
        
        # Calculate and display the percentage change if ref_value is provided
        if ref_value is not None and yval != ref_value:
            pct_change = ((yval - ref_value) / ref_value) * 100
            plt.text(bar.get_x() + bar.get_width()/2, yval / 2, f"{pct_change:+.1f}%", va='center', ha='center', color='white')

    plt.ylabel(ylabel, fontsize=14)
    plt.xticks(ticks=range(len(bar_names)), labels=bar_names, rotation=0, fontsize=14)
    plt.title(title)
    plt.tight_layout()
    plt.show()
    
# Initialize your parameters
#csv_prefixes = ["Office_totalBaseline", "Commercial_Shading", "Commercial_DayVent", "Commercial_AllVent", "Commercial_AllVent_mass"]



