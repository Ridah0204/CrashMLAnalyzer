import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TooltipProps } from 'recharts';


const VehicleDamageLineChart = () => {
  // Data restructured for line chart
  const data = [
    { 
      year: 2019, 
      "Unknown": 19, 
      "None": 14, 
      "Minor": 74, 
      "Moderate": 0, 
      "Major": 1 
    },
    { 
      year: 2020, 
      "Unknown": 8, 
      "None": 8, 
      "Minor": 27, 
      "Moderate": 0, 
      "Major": 1 
    },
    { 
      year: 2021, 
      "Unknown": 15, 
      "None": 6, 
      "Minor": 95, 
      "Moderate": 0, 
      "Major": 1 
    },
    { 
      year: 2022, 
      "Unknown": 8, 
      "None": 1, 
      "Minor": 47, 
      "Moderate": 0, 
      "Major": 2 
    },
    { 
      year: 2023, 
      "Unknown": 20, 
      "None": 10, 
      "Minor": 95, 
      "Moderate": 0, 
      "Major": 6 
    },
    { 
      year: 2024, 
      "Unknown": 12, 
      "None": 5, 
      "Minor": 38, 
      "Moderate": 0, 
      "Major": 0 
    }
  ];

  // Color mapping for damage types
  const colorMap = {
    "Unknown": "#808080", // Gray
    "None": "#4682B4",    // Steel Blue
    "Minor": "#32CD32",   // Lime Green
    "Moderate": "#FFA500", // Orange
    "Major": "#DC143C"    // Crimson
  };

  // Line thickness and point size configuration
  const lineConfig = {
    "Unknown": { strokeWidth: 2, dot: { r: 4 } },
    "None": { strokeWidth: 2, dot: { r: 4 } },
    "Minor": { strokeWidth: 3, dot: { r: 5 } },
    "Moderate": { strokeWidth: 2, dot: { r: 4 } },
    "Major": { strokeWidth: 2, dot: { r: 4 } }
  };

  // Custom tooltip to display more information
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-2 border border-gray-300 rounded shadow">
          <p className="font-semibold">Year: {label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-full p-4">
      <h2 className="text-xl font-bold text-center mb-4">Vehicle Damage by Year (2019-2024)</h2>
      <ResponsiveContainer width="100%" height={500}>
        <LineChart
          data={data}
          margin={{ top: 20, right: 30, bottom: 20, left: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="year" 
            label={{ value: 'Year', position: 'insideBottomRight', offset: -5 }}
            padding={{ left: 30, right: 30 }}
          />
          <YAxis 
            label={{ value: 'Count', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            verticalAlign="top" 
            height={36}
          />
          
          {Object.keys(colorMap).map(type => (
            <Line
              key={type}
              type="monotone"
              dataKey={type}
              name={type}
              stroke={colorMap[type]}
              activeDot={{ r: 8 }}
              strokeWidth={lineConfig[type].strokeWidth}
              dot={lineConfig[type].dot}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
      <div className="text-center text-sm text-gray-600 mt-4">
        <p>Data based on vehicle damage reports from 2019 to 2024</p>
      </div>
    </div>
  );
};

export default VehicleDamageLineChart;
