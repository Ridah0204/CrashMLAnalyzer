import Papa from 'papaparse';

export async function processRoadConditionsData(files) {
  // Define the road conditions we're looking for
  const roadConditionTypes = [
    'road_conditions_a_1',
    'road_conditions_b_1',
    'road_conditions_c_1',
    'road_conditions_d_1',
    'road_conditions_e_1',
    'road_conditions_f_1',
    'road_conditions_g_1',
    'road_conditions_h_1'
  ];
  
  // Initialize counters
  const conditionCounts = {};
  roadConditionTypes.forEach(type => {
    conditionCounts[type] = 0;
  });
  
  let totalRecords = 0;
  
  // Process each file
  for (const file of files) {
    try {
      const results = await new Promise((resolve, reject) => {
        Papa.parse(file, {
          header: true,
          skipEmptyLines: true,
          complete: resolve,
          error: reject
        });
      });
      
      totalRecords += results.data.length;
      
      // Count road conditions
      for (const row of results.data) {
        const condition = row.road_conditions;
        if (roadConditionTypes.includes(condition)) {
          conditionCounts[condition]++;
        }
      }
    } catch (error) {
      console.error(`Error processing file:`, error.message);
    }
  }
  
  // Create mapping for labels
  const conditionLabels = {
    'road_conditions_a_1': 'Holes, Deep Rut',
    'road_conditions_b_1': 'Loose Material on Roadway',
    'road_conditions_c_1': 'Obstruction on Roadway',
    'road_conditions_d_1': 'Construction-Repair Zone',
    'road_conditions_e_1': 'Reduced Roadway Width',
    'road_conditions_f_1': 'Flooded',
    'road_conditions_g_1': 'Other',
    'road_conditions_h_1': 'No Unusual Conditions'
  };
  
  // Format data for visualization
  const chartData = roadConditionTypes.map(type => ({
    id: type,
    label: conditionLabels[type],
    count: conditionCounts[type]
  }));
  
  return { 
    counts: conditionCounts,
    labels: conditionLabels,
    chartData: chartData,
    totalRecords: totalRecords
  };
}