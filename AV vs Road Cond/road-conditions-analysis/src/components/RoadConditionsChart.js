import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LabelList, ResponsiveContainer } from 'recharts';
import { processRoadConditionsData } from '../processData';

const RoadConditionsChart = () => {
  const [data, setData] = useState([]);
  const [totalRecords, setTotalRecords] = useState(0);

  useEffect(() => {
    // In a real application, you would load the CSV files here
    // For this example, we'll use the pre-processed data
    setData([
      {id: "road_conditions_a_1", label: "Holes, Deep Rut", count: 1},
      {id: "road_conditions_b_1", label: "Loose Material on Roadway", count: 3},
      {id: "road_conditions_c_1", label: "Obstruction on Roadway", count: 1},
      {id: "road_conditions_d_1", label: "Construction-Repair Zone", count: 0},
      {id: "road_conditions_e_1", label: "Reduced Roadway Width", count: 1},
      {id: "road_conditions_f_1", label: "Flooded", count: 0},
      {id: "road_conditions_g_1", label: "Other", count: 8},
      {id: "road_conditions_h_1", label: "No Unusual Conditions", count: 46}
    ]);
    setTotalRecords(563);
  }, []);

  // Sort data to display in descending order by count
  const sortedData = [...data].sort((a, b) => b.count - a.count);
  
  // Create shortened labels for the x-axis to prevent overlap
  const shortenedData = sortedData.map(item => ({
    ...item,
    shortLabel: item.label.length > 15 ? item.label.substring(0, 15) + '...' : item.label
  }));

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4 text-center">Road Conditions Analysis</h2>
      <div className="bg-white p-4 rounded-lg shadow">
        <ResponsiveContainer width="100%" height={500}>
          <BarChart
            data={shortenedData}
            margin={{
              top: 20,
              right: 30,
              left: 20,
              bottom: 120
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="shortLabel" 
              angle={-45} 
              textAnchor="end" 
              height={100}
              interval={0}
            />
            <YAxis />
            <Tooltip 
              formatter={(value, name, props) => [value, 'Count']}
              labelFormatter={(value) => {
                const item = shortenedData.find(d => d.shortLabel === value);
                return item ? item.label : value;
              }}
            />
            <Legend />
            <Bar dataKey="count" fill="#8884d8" name="Occurrence Count">
              <LabelList dataKey="count" position="top" />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        
        <div className="mt-6">
          <h3 className="text-xl font-semibold mb-2">Legend Key</h3>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {data.map(item => (
              <li key={item.id} className="flex items-start">
                <span className="w-4 h-4 mt-1 mr-2 inline-block bg-blue-500"></span>
                <span><strong>{item.id}:</strong> {item.label} ({item.count})</span>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="mt-6 text-sm text-gray-600">
          <p>Total records analyzed: {totalRecords}</p>
          <p>Most common condition: {sortedData[0]?.label} ({sortedData[0]?.count} occurrences)</p>
          <p>Least common conditions: {sortedData.filter(item => item.count === 0).map(item => item.label).join(' and ')} (0 occurrences each)</p>
        </div>
      </div>
    </div>
  );
};

export default RoadConditionsChart;