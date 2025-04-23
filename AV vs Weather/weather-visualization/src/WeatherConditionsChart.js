// WeatherConditionsChart.js
import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import Papa from 'papaparse';

const WeatherConditionsChart = () => {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Define the weather condition mapping
  const weatherMapping = {
    'weather_a_1': 'Clear',
    'weather_b_1': 'Cloudy',
    'weather_c_1': 'Raining',
    'weather_d_1': 'Snowing',
    'weather_e_1': 'Fog/Visibility',
    'weather_f_1': 'Other',
    'weather_g_1': 'Wind'
  };

  // Define colors for each weather condition
  const colorMapping = {
    'weather_a_1': '#4FC3F7', // Light blue for clear
    'weather_b_1': '#90A4AE', // Gray for cloudy
    'weather_c_1': '#1976D2', // Blue for rain
    'weather_d_1': '#B3E5FC', // Very light blue for snow
    'weather_e_1': '#CFD8DC', // Very light gray for fog
    'weather_f_1': '#78909C', // Dark gray for other
    'weather_g_1': '#26A69A'  // Teal for wind
  };

  useEffect(() => {
    const loadData = async () => {
      try {
        // List of CSV files to process
        const files = [
          'processed_crash_data_2019.csv',
          'processed_crash_data_2020.csv',
          'processed_crash_data_2021.csv',
          'processed_crash_data_2022.csv',
          'processed_crash_data_2023.csv',
          'processed_crash_data_2024.csv',
          'processed_crash_data_22024.csv'
        ];

        // Initialize weather condition counts
        const totalCounts = {
          'weather_a_1': 0,
          'weather_b_1': 0,
          'weather_c_1': 0,
          'weather_d_1': 0,
          'weather_e_1': 0,
          'weather_f_1': 0,
          'weather_g_1': 0
        };

        // Process each file
        for (const filename of files) {
          try {
            // Fetch the CSV file
            const response = await fetch(filename);
            
            if (!response.ok) {
              console.warn(`Could not load ${filename}: ${response.status} ${response.statusText}`);
              continue; // Skip this file and continue with others
            }
            
            const csvText = await response.text();
            
            // Parse the CSV
            const results = Papa.parse(csvText, {
              header: true,
              skipEmptyLines: true
            });
            
            // Count weather conditions
            results.data.forEach(row => {
              if (row.weather_conditions) {
                const weatherStr = row.weather_conditions.trim();
                
                // Check for each possible weather condition
                Object.keys(totalCounts).forEach(code => {
                  if (weatherStr.includes(code)) {
                    totalCounts[code] += 1;
                  }
                });
                
                // If none of our codes match, count as Other
                if (!Object.keys(totalCounts).some(code => weatherStr.includes(code))) {
                  totalCounts['weather_f_1'] += 1;
                }
              }
            });
            
            console.log(`Processed ${filename}`);
          } catch (error) {
            console.error(`Error processing ${filename}:`, error);
          }
        }

        // Format data for the chart
        const formattedData = Object.entries(totalCounts).map(([code, count]) => ({
          code,
          name: weatherMapping[code],
          count,
          color: colorMapping[code]
        }));

        setChartData(formattedData);
        setLoading(false);
      } catch (error) {
        console.error('Error loading data:', error);
        setError('Failed to load weather condition data');
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading weather data...</div>;
  }

  if (error) {
    return <div className="text-red-600 p-4">{error}</div>;
  }

  return (
    <div className="flex flex-col items-center w-full p-4">
      <h2 className="text-2xl font-bold mb-4">Weather Conditions in Accident Reports (2019-2024)</h2>
      
      <div className="w-full max-w-4xl mb-6">
        <ResponsiveContainer width="100%" height={400}>
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 70 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="name" 
              angle={-45} 
              textAnchor="end" 
              height={70} 
              tick={{ fontSize: 14 }}
            />
            <YAxis 
              label={{ value: 'Number of Accidents', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              formatter={(value, name, props) => [`${value} accidents`, props.payload.name]}
              labelFormatter={(label) => `Weather: ${label}`}
            />
            <Legend />
            <Bar dataKey="count" name="Number of Accidents">
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="w-full max-w-4xl bg-gray-50 p-4 rounded-lg border border-gray-200">
        <h3 className="text-xl font-semibold mb-2">Weather Condition Code Key</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {chartData.map((item) => (
            <div key={item.code} className="flex items-center">
              <div 
                className="w-6 h-6 mr-2" 
                style={{ backgroundColor: item.color }}
              ></div>
              <div>
                <span className="font-medium">{item.code}:</span> {item.name} ({item.count} accidents)
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WeatherConditionsChart;