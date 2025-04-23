import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import _ from 'lodash';

const AutoManufacturerTimeline = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Function to extract year from date string
  const extractYear = (dateString) => {
    if (!dateString || typeof dateString !== 'string') return null;
    
    // Format: MM/DD/YYYY
    const match1 = dateString.match(/\d{1,2}\/\d{1,2}\/(\d{4})/);
    if (match1) return parseInt(match1[1]);
    
    // Format: YYYY-MM-DD
    const match2 = dateString.match(/^(\d{4})-\d{1,2}-\d{1,2}/);
    if (match2) return parseInt(match2[1]);
    
    return null;
  };
  
  // Normalize make names
  const normalizeMake = (make) => {
    if (!make) return '';
    make = make.trim();
    
    // Handle variations of Mercedes-Benz
    if (make === 'Mercedes' || make === 'Benz' || make === 'Mercedes Benz') {
      return 'Mercedes-Benz';
    }
    
    // Keep Nissan with a space distinct
    if (make === 'Nissan ') {
      return 'Nissan ';
    }
    
    return make;
  };
  
  // Manufacturer colors and information
  const manufacturerInfo = {
    'Toyota': { color: '#EB0A1E', textColor: 'white', abbr: 'TOY' },
    'Lexus': { color: '#1A1A1A', textColor: 'white', abbr: 'LEX' },
    'Lincoln': { color: '#002D5B', textColor: 'white', abbr: 'LIN' },
    'Chevrolet': { color: '#D1B962', textColor: 'black', abbr: 'CHV' },
    'Ford': { color: '#003478', textColor: 'white', abbr: 'FOR' },
    'Chrysler': { color: '#0C2340', textColor: 'white', abbr: 'CHR' },
    'Autonomous': { color: '#7F7F7F', textColor: 'white', abbr: 'AUT' },
    'Hyundai': { color: '#003D7D', textColor: 'white', abbr: 'HYU' },
    'Cruise': { color: '#4B96F3', textColor: 'white', abbr: 'CRU' },
    'Jaguar': { color: '#175129', textColor: 'white', abbr: 'JAG' },
    'Nissan': { color: '#C3002F', textColor: 'white', abbr: 'NIS' },
    'Nissan ': { color: '#C3002F', textColor: 'white', abbr: 'NIS ' },
    'Mercedes-Benz': { color: '#00ADEF', textColor: 'black', abbr: 'MRC' },
    'Navya': { color: '#001E60', textColor: 'white', abbr: 'NAV' },
    'Zoox': { color: '#6EC5B8', textColor: 'black', abbr: 'ZOX' },
    'BMW': { color: '#0066B1', textColor: 'white', abbr: 'BMW' },
    'GM': { color: '#0170CE', textColor: 'white', abbr: 'GM' },
    'Volvo': { color: '#003057', textColor: 'white', abbr: 'VOL' },
    'Honda': { color: '#CC0000', textColor: 'white', abbr: 'HON' },
    'Kia': { color: '#BB162B', textColor: 'white', abbr: 'KIA' },
    'Audi': { color: '#000000', textColor: 'white', abbr: 'AUD' },
    'Tesla': { color: '#E82127', textColor: 'white', abbr: 'TES' },
    'Waymo': { color: '#00A9E0', textColor: 'black', abbr: 'WAY' },
    'Uber': { color: '#000000', textColor: 'white', abbr: 'UBR' }
  };
  
  // Files to process
  const filesToProcess = [
    'processed_crash_data_2019.csv',
    'processed_crash_data_2020.csv', 
    'processed_crash_data_2021.csv',
    'processed_crash_data_2022.csv',
    'processed_crash_data_2023.csv',
    'processed_crash_data_2024.csv',
    'processed_crash_data_22024.csv'
  ];
  
  useEffect(() => {
    const processAllFiles = async () => {
      try {
        setLoading(true);
        
        // Process each file and combine the data
        const combinedData = [];
        
        for (const file of filesToProcess) {
          try {
            const fileContent = await window.fs.readFile(file, { encoding: 'utf8' });
            
            Papa.parse(fileContent, {
              header: true,
              dynamicTyping: true,
              skipEmptyLines: true,
              complete: (results) => {
                // Process the records
                results.data.forEach(record => {
                  let year = null;
                  
                  // Try to extract year from date
                  if (record.date) {
                    year = extractYear(record.date);
                  }
                  
                  // If that fails, try to extract from the filename
                  if (!year) {
                    const yearMatch = file.match(/(\d{4})/);
                    if (yearMatch) {
                      year = parseInt(yearMatch[1]);
                    }
                  }
                  
                  // Skip if no year determined
                  if (!year) return;
                  
                  // Get the vehicle make
                  let make = record.vehicle_1_make || record.MAkE;
                  if (!make) return;
                  
                  make = normalizeMake(make);
                  
                  // Add to our dataset
                  combinedData.push({
                    year,
                    make,
                    autonomous: record.autonomous_mode && 
                               record.autonomous_mode.toLowerCase() === 'yes'
                  });
                });
              }
            });
          } catch (err) {
            console.error(`Error processing ${file}:`, err);
          }
        }
        
        // Group and count the data
        const groupedData = _.groupBy(combinedData, 'year');
        
        // Transform into format needed for visualization
        const transformedData = [];
        Object.keys(groupedData).forEach(year => {
          const yearRecords = groupedData[year];
          
          // Count by manufacturer
          const makeCount = {};
          const autonomousCount = {};
          
          yearRecords.forEach(record => {
            if (!makeCount[record.make]) {
              makeCount[record.make] = 0;
              autonomousCount[record.make] = 0;
            }
            
            makeCount[record.make]++;
            
            if (record.autonomous) {
              autonomousCount[record.make]++;
            }
          });
          
          // Add to our transformed dataset
          Object.keys(makeCount).forEach(make => {
            transformedData.push({
              year: parseInt(year),
              make,
              count: makeCount[make],
              autonomous: autonomousCount[make]
            });
          });
        });
        
        setData(transformedData);
        setLoading(false);
      } catch (err) {
        setError(`Error loading data: ${err.message}`);
        setLoading(false);
      }
    };
    
    processAllFiles();
  }, []);
  
  // Component for manufacturer logo
  const ManufacturerLogo = ({ make, count, autonomous, isAutonomous }) => {
    const info = manufacturerInfo[make] || { 
      color: '#888888', 
      textColor: 'white', 
      abbr: make.substring(0, 3).toUpperCase() 
    };
    
    // Logo paths for each manufacturer
    const logoMap = {
      'Toyota': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cellipse cx='50' cy='50' rx='45' ry='25' fill='%23EB0A1E' /%3E%3Cellipse cx='50' cy='50' rx='24' ry='14' fill='white' /%3E%3Cellipse cx='50' cy='50' rx='35' ry='10' fill='none' stroke='white' stroke-width='2' /%3E%3C/svg%3E",
      'Lexus': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%231A1A1A' /%3E%3Cpath d='M30,50 L70,50 M50,30 L50,70' stroke='silver' stroke-width='6' /%3E%3Cpath d='M35,35 L65,65 M35,65 L65,35' stroke='silver' stroke-width='3' /%3E%3C/svg%3E",
      'Lincoln': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect x='20' y='20' width='60' height='60' fill='%23002D5B' /%3E%3Ctext x='50' y='65' font-family='Arial' font-size='40' font-weight='bold' fill='white' text-anchor='middle'%3EL%3C/text%3E%3C/svg%3E",
      'Chevrolet': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M20,35 L50,20 L80,35 L80,65 L50,80 L20,65 Z' fill='%23D1B962' /%3E%3Cpath d='M30,40 L50,30 L70,40 L70,60 L50,70 L30,60 Z' fill='none' stroke='%23000000' stroke-width='3' /%3E%3C/svg%3E",
      'Ford': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cellipse cx='50' cy='50' rx='40' ry='25' fill='%23003478' /%3E%3Ctext x='50' y='60' font-family='Arial' font-size='30' font-weight='bold' fill='white' text-anchor='middle'%3EFORD%3C/text%3E%3C/svg%3E",
      'Chrysler': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%230C2340' /%3E%3Ctext x='50' y='60' font-family='Arial' font-size='18' font-weight='bold' fill='white' text-anchor='middle'%3ECHRYSLER%3C/text%3E%3C/svg%3E",
      'Autonomous': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%237F7F7F' /%3E%3Cpath d='M30,50 C30,40 40,30 50,30 C60,30 70,40 70,50 C70,60 60,70 50,70 C40,70 30,60 30,50 Z' fill='none' stroke='white' stroke-width='3' /%3E%3Ccircle cx='40' cy='45' r='5' fill='white' /%3E%3Ccircle cx='60' cy='45' r='5' fill='white' /%3E%3C/svg%3E",
      'Hyundai': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cellipse cx='50' cy='50' rx='40' ry='30' fill='%23003D7D' /%3E%3Ctext x='50' y='60' font-family='Arial' font-size='18' font-weight='bold' fill='white' text-anchor='middle'%3EH%3C/text%3E%3C/svg%3E",
      'Cruise': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%234B96F3' /%3E%3Cpath d='M30,60 C30,40 40,30 50,30 C70,30 70,50 70,50 C70,70 60,70 50,70 C30,70 30,60 30,60 Z' fill='none' stroke='white' stroke-width='3' /%3E%3C/svg%3E",
      'Jaguar': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%23175129' /%3E%3Cpath d='M30,50 L70,50 M30,40 L70,40 M30,60 L70,60' stroke='silver' stroke-width='3' /%3E%3Cpath d='M40,30 L40,70 M50,30 L50,70 M60,30 L60,70' stroke='silver' stroke-width='2' /%3E%3C/svg%3E",
      'Nissan': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%23C3002F' /%3E%3Ccircle cx='50' cy='50' r='35' fill='none' stroke='silver' stroke-width='3' /%3E%3Ctext x='50' y='60' font-family='Arial' font-size='20' font-weight='bold' fill='silver' text-anchor='middle'%3EN%3C/text%3E%3C/svg%3E",
      'Nissan ': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%23C3002F' /%3E%3Ccircle cx='50' cy='50' r='35' fill='none' stroke='silver' stroke-width='3' /%3E%3Ctext x='50' y='60' font-family='Arial' font-size='20' font-weight='bold' fill='silver' text-anchor='middle'%3EN*%3C/text%3E%3C/svg%3E",
      'Mercedes-Benz': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%2300ADEF' /%3E%3Ccircle cx='50' cy='50' r='30' fill='white' /%3E%3Cpath d='M50,20 L50,80 M20,50 L80,50 M28.6,28.6 L71.4,71.4 M28.6,71.4 L71.4,28.6' stroke='%2300ADEF' stroke-width='3' /%3E%3C/svg%3E",
      'Navya': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect x='20' y='30' width='60' height='40' fill='%23001E60' /%3E%3Ctext x='50' y='58' font-family='Arial' font-size='18' font-weight='bold' fill='white' text-anchor='middle'%3ENAVYA%3C/text%3E%3C/svg%3E",
      'Zoox': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%236EC5B8' /%3E%3Ctext x='50' y='60' font-family='Arial' font-size='25' font-weight='bold' fill='black' text-anchor='middle'%3EZ%3C/text%3E%3C/svg%3E",
      'BMW': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='white' stroke='black' stroke-width='2' /%3E%3Cpath d='M50,10 A40,40 0 0,1 90,50 L50,50 Z' fill='%230066B1' /%3E%3Cpath d='M50,10 A40,40 0 0,0 10,50 L50,50 Z' fill='%230066B1' /%3E%3Cpath d='M50,90 A40,40 0 0,0 10,50 L50,50 Z' fill='white' /%3E%3Cpath d='M50,90 A40,40 0 0,1 90,50 L50,50 Z' fill='white' /%3E%3C/svg%3E",
      'GM': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect x='20' y='30' width='60' height='40' fill='%230170CE' /%3E%3Ctext x='50' y='58' font-family='Arial' font-size='25' font-weight='bold' fill='white' text-anchor='middle'%3EGM%3C/text%3E%3C/svg%3E",
      'Volvo': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%23003057' /%3E%3Ccircle cx='50' cy='50' r='38' fill='none' stroke='silver' stroke-width='2' /%3E%3Cpath d='M30,50 L70,50' stroke='silver' stroke-width='3' /%3E%3Cpath d='M50,30 L50,70' stroke='silver' stroke-width='3' /%3E%3C/svg%3E",
      'Honda': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect x='20' y='30' width='60' height='40' rx='5' ry='5' fill='%23CC0000' /%3E%3Ctext x='50' y='58' font-family='Arial' font-size='25' font-weight='bold' fill='white' text-anchor='middle'%3EH%3C/text%3E%3C/svg%3E",
      'Kia': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cellipse cx='50' cy='50' rx='40' ry='25' fill='%23BB162B' /%3E%3Ctext x='50' y='58' font-family='Arial' font-size='25' font-weight='bold' fill='white' text-anchor='middle'%3EKIA%3C/text%3E%3C/svg%3E",
      'Audi': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='30' cy='50' r='15' fill='%23000000' stroke='silver' stroke-width='2' /%3E%3Ccircle cx='50' cy='50' r='15' fill='%23000000' stroke='silver' stroke-width='2' /%3E%3Ccircle cx='70' cy='50' r='15' fill='%23000000' stroke='silver' stroke-width='2' /%3E%3Ccircle cx='90' cy='50' r='15' fill='%23000000' stroke='silver' stroke-width='2' /%3E%3C/svg%3E",
      'Tesla': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M20,50 L50,20 L80,50 L65,50 L50,35 L35,50 Z' fill='%23E82127' /%3E%3Cpath d='M35,50 L50,65 L65,50 L80,50 L50,80 L20,50 Z' fill='%23E82127' /%3E%3C/svg%3E",
      'Waymo': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%2300A9E0' /%3E%3Cpath d='M30,40 L70,40 L50,70 Z' fill='white' /%3E%3C/svg%3E",
      'Uber': "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%23000000' /%3E%3Ctext x='50' y='60' font-family='Arial' font-size='25' font-weight='bold' fill='white' text-anchor='middle'%3EU%3C/text%3E%3C/svg%3E"
    };
    
    return (
      <div className="flex flex-col items-center justify-center mx-2">
        <div 
          className={`w-10 h-10 rounded-full flex items-center justify-center overflow-hidden`}
          style={{ 
            border: autonomous > 0 ? '2px dashed #00ff00' : 'none'
          }}
        >
          <img 
            src={logoMap[make] || `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='${info.color}' /%3E%3Ctext x='50' y='60' font-family='Arial' font-size='25' font-weight='bold' fill='${info.textColor}' text-anchor='middle'%3E${info.abbr}%3C/text%3E%3C/svg%3E`}
            alt={make}
            className="w-full h-full object-cover"
          />
        </div>
        <div className="text-xs text-center mt-1">{make}</div>
        <div className="text-xs text-center mt-1">{count}</div>
        {autonomous > 0 && (
          <div className="text-xs text-green-600 text-center">{autonomous}</div>
        )}
      </div>
    );
  };
  
  if (loading) return <div className="p-8 text-center">Loading data...</div>;
  if (error) return <div className="p-8 text-center text-red-500">{error}</div>;
  
  // Get years that have data
  const yearsWithData = [...new Set(data.map(item => item.year))].sort();
  
  // Group data by year and make
  const dataByYear = {};
  yearsWithData.forEach(year => {
    dataByYear[year] = {};
  });
  
  data.forEach(item => {
    if (!dataByYear[item.year]) return;
    dataByYear[item.year][item.make] = { 
      count: item.count, 
      autonomous: item.autonomous 
    };
  });
  
  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h1 className="text-xl font-bold mb-4 text-center">Autonomous Vehicle Make - Collision Reports (2019-2024)</h1>
      
      {/* Legend - Only for autonomous mode */}
      <div className="mb-4 flex justify-end items-center">
        <div className="flex items-center">
          <div className="w-4 h-4 rounded-full border-2 border-dashed border-green-500 mr-1"></div>
          <span className="text-sm">Autonomous Mode</span>
        </div>
      </div>
      
      {/* Timeline as rows with manufacturers in each row */}
      <div className="border rounded-lg">
        {yearsWithData.map(year => {
          const yearData = dataByYear[year];
          
          // Get manufacturers and sort them by count (lowest to highest)
          const manufacturers = Object.keys(yearData)
            .map(make => ({
              make,
              count: yearData[make].count,
              autonomous: yearData[make].autonomous
            }))
            .sort((a, b) => a.count - b.count)
            .map(item => item.make);
          
          return (
            <div key={`row-${year}`} className="border-b last:border-b-0 p-3">
              <div className="flex items-center">
                <div className="font-bold text-lg mr-4 min-w-12">{year}</div>
                <div className="flex flex-wrap">
                  {manufacturers.map(make => (
                    <ManufacturerLogo 
                      key={`${year}-${make}`}
                      make={make}
                      count={yearData[make].count}
                      autonomous={yearData[make].autonomous}
                      isAutonomous={yearData[make].autonomous > 0}
                    />
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-4 text-sm text-gray-600 text-center">
        Note: Manufacturers are arranged from lowest count (left) to highest count (right) within each year.
      </div>
    </div>
  );
};

export default AutoManufacturerTimeline;