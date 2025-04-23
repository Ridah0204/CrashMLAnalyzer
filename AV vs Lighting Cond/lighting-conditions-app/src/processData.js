const fs = require('fs');
const Papa = require('papaparse');

// Define the lighting conditions mapping
const lightingConditionMap = {
    'lighting_a_1': 'Daylight',
    'lighting_b_1': 'Dusk-Dawn',
    'lighting_c_1': 'Dark-Street Lights',
    'lighting_d_1': 'Dark-No Street Lights',
    'lighting_e_1': 'Dark-Street Lights Not Functioning'
};

// Initialize counts structure
const lightingCounts = {
    'lighting_a_1': 0,
    'lighting_b_1': 0,
    'lighting_c_1': 0,
    'lighting_d_1': 0,
    'lighting_e_1': 0
};

// List of CSV files to process
const fileNames = [
    'processed_crash_data_2019.csv',
    'processed_crash_data_2020.csv',
    'processed_crash_data_2021.csv',
    'processed_crash_data_2022.csv',
    'processed_crash_data_2023.csv',
    'processed_crash_data_2024.csv',
    'processed_crash_data_22024.csv'
];

// Process all files
function processAllFiles() {
    for (const fileName of fileNames) {
        try {
            // Read the file synchronously
            const fileContent = fs.readFileSync(fileName, 'utf8');
            
            // Parse the CSV
            const parsedData = Papa.parse(fileContent, {
                header: true,
                skipEmptyLines: true
            });
            
            // Process the data
            parsedData.data.forEach(row => {
                if (row.lighting_conditions) {
                    // Check for exact matches first
                    if (row.lighting_conditions in lightingCounts) {
                        lightingCounts[row.lighting_conditions]++;
                    } 
                    // Check for partial matches (when the field contains multiple conditions)
                    else {
                        Object.keys(lightingCounts).forEach(condition => {
                            if (row.lighting_conditions.includes(condition)) {
                                lightingCounts[condition]++;
                            }
                        });
                    }
                }
            });
        } catch (error) {
            console.error(`Error processing file ${fileName}:`, error);
        }
    }
    
    // Print the results
    console.log("Lighting Condition Counts:");
    for (const [condition, count] of Object.entries(lightingCounts)) {
        console.log(`${condition} (${lightingConditionMap[condition]}): ${count}`);
    }
    
    // Generate JSON output to use in a chart
    const chartData = {
        labels: Object.keys(lightingCounts).map(key => lightingConditionMap[key]),
        values: Object.values(lightingCounts)
    };
    
    // Write the chart data to a JSON file for use in your HTML
    fs.writeFileSync('lighting-condition-data.json', JSON.stringify(chartData, null, 2));
    console.log('Data written to lighting-condition-data.json');
}

// Run the processing
processAllFiles();