from flask import Flask, request, render_template, url_for
import os
from SimManagement import gen_idf_run_sim
from Post_proc import create_bar_chart2, load_and_process_data, calculate_pmv
import pandas as pd
from save_to_db import create_table_for_yearly_data_insert 


#__________________________________________________________________________________
#Set weather file directory
#__________________________________________________________________________________
weather_Folder="Weather"

if not(os.path.exists(weather_Folder)):
    os.makedirs(weather_Folder)

Sim_dir="Simulations"
#__________________________________________________________________________________
#Start client connection
#__________________________________________________________________________________
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('Input_web_form.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Handle file upload
    if 'weatherFile' in request.files:
        file = request.files['weatherFile']
        epwfile=os.path.join(os.path.dirname(os.path.realpath(__file__)),weather_Folder, file.filename)
        if not(os.path.exists(epwfile)):
            file.save(epwfile)  # save file
            

    # Process other form data
    building_type = request.form.get('buildingType')
    window_orientation = request.form.get('windowOrientation')

    # Check if simulation was done before
    epw_name=file.filename.split(".epw")[0]
    file_name_true = epw_name + '_' + building_type + '_' + window_orientation + '_' + 'True' + '.png'
    file_name_false = epw_name + '_' + building_type + '_' + window_orientation + '_' + 'False' + '.png'

    exists_true = os.path.exists(os.path.join('static',file_name_true))
    exists_false = os.path.exists(os.path.join('static',file_name_false))

    if exists_true:
        pngpath=file_name_true #AC needed
    elif exists_false:
        pngpath=file_name_false #AC not needed

    else:#Simulation needs to be run
        # IDF gen and simulation
        #__________________________________________________________________________________
        csv_prefixes=gen_idf_run_sim(Sim_dir,building_type,window_orientation,epwfile)

        # Load Results and Calculate comofrt metrics (PMV)
        #__________________________________________________________________________________
        csv_file_paths = [os.path.join(Sim_dir, prefix + "out.csv") for prefix in csv_prefixes]
        ambient_prefix="weatherData"
        nested_dict = load_and_process_data(csv_file_paths,"weatherData")
        PMV_too_hot=0.5
        nested_dict=calculate_pmv(nested_dict, vr=0.1, met=1, clo=0.5, PMV_too_hot=PMV_too_hot) # Calculate PMV

        # Save the annual PMV "too hot" data to database
        #__________________________________________________________________________________
        variants = [prefix.split('_', 1)[1] for prefix in csv_prefixes]
        table_name = epw_name + '_' + building_type + '_' + window_orientation
        table_name = table_name.replace('.', '') #naming convention for db, no dots allowed
        table_name = table_name.replace('-', '_') #naming convention for db, no dots allowed
        #create_table_for_yearly_data_insert('Comfort.db', table_name, variants, nested_dict) #commneted out for now, but working for future extension
        
        # Data Visualization
        #__________________________________________________________________________________
        uncomfortable_sums_pmv = {prefix: df['too_hot'].sum() for prefix, df in nested_dict.items()} # Summarize uncomfortable hours from PMV 
        prefixes = list(uncomfortable_sums_pmv.keys())
        uncomfortable_counts_pmv = list(uncomfortable_sums_pmv.values())
        bar_names = ['Baseline', '+Shading', '+Vent. Day', '+Vent. Night', '+Thermal Mass']
        filename_base=epw_name + '_' + building_type + '_' + window_orientation
        pngpath=create_bar_chart2(uncomfortable_counts_pmv[1:], bar_names, 'Hours with PMV > ' + str(PMV_too_hot), 'blue', None, ref_value=uncomfortable_counts_pmv[1],tolerance_PMV=20, filename_base=filename_base)

        
    # Return to client
    #__________________________________________________________________________________       

    boolean_part = pngpath.rsplit('.', 1)[0].split('_')[-1] #supply if AC is needed to the template
    if boolean_part == 'True':
        AC_needed = 'Yes'
    else:
        AC_needed = 'No'
    
    fig_path = url_for('static',filename=pngpath) # Assuming the image is in a folder named 'static/images'

    return render_template('submission_result.html', file_name=file.filename, building_type=building_type, window_orientation=window_orientation,fig_path=fig_path,AC_needed=AC_needed)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, debug=True) # Run on port 3000


