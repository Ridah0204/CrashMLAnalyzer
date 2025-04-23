import React from 'react';
import { ChevronRight, Database, List, FileText, BarChart2, Brain, Car, AlertTriangle } from 'lucide-react';

const TitleSlide = () => {
  return (
    <div className="flex flex-col h-full w-full bg-gradient-to-br from-blue-900 to-blue-700 text-white p-8 rounded-lg shadow-lg">
      <div className="flex justify-center items-center flex-1">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-6">Unraveling Responsibility</h1>
          <h2 className="text-2xl mb-8">Investigating Accident Causality in Autonomous Vehicles</h2>
          
          <div className="flex justify-center mb-10">
            <Car size={80} className="text-blue-300" />
          </div>
          
          <div className="mb-4">
            <p className="text-xl">Florida Perfect Rwejuna</p>
            <p className="text-sm mt-2">Honors Senior Research Project</p>
            <p className="text-sm mt-1">April 14, 2025</p>
          </div>
          
          <div className="mt-8">
            <p className="text-sm">Advisors:</p>
            <p className="text-sm mt-1">Dr. Alae Loukilli • Dr. Nishat Majid • Mithun Goutham</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const ModelArchitecture = () => {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-2xl font-bold text-blue-800 mb-6">CrashML Model Architecture</h2>
      
      <div className="flex flex-col space-y-6">
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-blue-100 p-4 rounded shadow">
            <h3 className="font-bold text-blue-700 mb-2">Data Processing</h3>
            <ul className="text-sm space-y-2">
              <li className="flex items-start">
                <ChevronRight size={16} className="text-blue-500 mt-1 mr-1 flex-shrink-0" />
                <span>DMV PDF extraction</span>
              </li>
              <li className="flex items-start">
                <ChevronRight size={16} className="text-blue-500 mt-1 mr-1 flex-shrink-0" />
                <span>Standardization of columns</span>
              </li>
              <li className="flex items-start">
                <ChevronRight size={16} className="text-blue-500 mt-1 mr-1 flex-shrink-0" />
                <span>Ground truth labeling</span>
              </li>
            </ul>
          </div>
          
          <div className="bg-blue-100 p-4 rounded shadow">
            <h3 className="font-bold text-blue-700 mb-2">Feature Engineering</h3>
            <ul className="text-sm space-y-2">
              <li className="flex items-start">
                <ChevronRight size={16} className="text-blue-500 mt-1 mr-1 flex-shrink-0" />
                <span>Structured features (9 binary)</span>
              </li>
              <li className="flex items-start">
                <ChevronRight size={16} className="text-blue-500 mt-1 mr-1 flex-shrink-0" />
                <span>Text features from descriptions</span>
              </li>
              <li className="flex items-start">
                <ChevronRight size={16} className="text-blue-500 mt-1 mr-1 flex-shrink-0" />
                <span>TF-IDF vectorization (200 features)</span>
              </li>
            </ul>
          </div>
          
          <div className="bg-blue-100 p-4 rounded shadow">
            <h3 className="font-bold text-blue-700 mb-2">Data Split</h3>
            <ul className="text-sm space-y-2">
              <li className="flex items-start">
                <ChevronRight size={16} className="text-blue-500 mt-1 mr-1 flex-shrink-0" />
                <span>80% Training data</span>
              </li>
              <li className="flex items-start">
                <ChevronRight size={16} className="text-blue-500 mt-1 mr-1 flex-shrink-0" />
                <span>10% Validation data</span>
              </li>
              <li className="flex items-start">
                <ChevronRight size={16} className="text-blue-500 mt-1 mr-1 flex-shrink-0" />
                <span>10% Testing data</span>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="flex justify-center bg-blue-50 p-6 rounded-lg">
          <div className="flex items-center space-x-4">
            <Database size={32} className="text-blue-700" />
            <div className="text-2xl font-bold text-blue-700">→</div>
            <FileText size={32} className="text-blue-700" />
            <div className="text-2xl font-bold text-blue-700">→</div>
            <List size={32} className="text-blue-700" />
            <div className="text-2xl font-bold text-blue-700">→</div>
            <Brain size={32} className="text-blue-700" />
            <div className="text-2xl font-bold text-blue-700">→</div>
            <BarChart2 size={32} className="text-blue-700" />
          </div>
        </div>
        
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-green-100 p-4 rounded shadow">
            <h3 className="font-bold text-green-700 mb-2">Random Forest</h3>
            <ul className="text-sm space-y-2">
              <li className="flex items-start">
                <ChevronRight size={16} className="text-green-500 mt-1 mr-1 flex-shrink-0" />
                <span>100 estimators</span>
              </li>
              <li className="flex items-start">
                <ChevronRight size={16} className="text-green-500 mt-1 mr-1 flex-shrink-0" />
                <span>Multi-class classification</span>
              </li>
              <li className="flex items-start">
                <ChevronRight size={16} className="text-green-500 mt-1 mr-1 flex-shrink-0" />
                <span>Feature importance analysis</span>
              </li>
            </ul>
          </div>
          
          <div className="bg-yellow-100 p-4 rounded shadow">
            <h3 className="font-bold text-yellow-700 mb-2">Gradient Boosting</h3>
            <ul className="text-sm space-y-2">
              <li className="flex items-start">
                <ChevronRight size={16} className="text-yellow-500 mt-1 mr-1 flex-shrink-0" />
                <span>Default parameters</span>
              </li>
              <li className="flex items-start">
                <ChevronRight size={16} className="text-yellow-500 mt-1 mr-1 flex-shrink-0" />
                <span>Sequential tree building</span>
              </li>
              <li className="flex items-start">
                <ChevronRight size={16} className="text-yellow-500 mt-1 mr-1 flex-shrink-0" />
                <span>Error minimization focus</span>
              </li>
            </ul>
          </div>
          
          <div className="bg-purple-100 p-4 rounded shadow">
            <h3 className="font-bold text-purple-700 mb-2">Logistic Regression</h3>
            <ul className="text-sm space-y-2">
              <li className="flex items-start">
                <ChevronRight size={16} className="text-purple-500 mt-1 mr-1 flex-shrink-0" />
                <span>One-vs-rest approach</span>
              </li>
              <li className="flex items-start">
                <ChevronRight size={16} className="text-purple-500 mt-1 mr-1 flex-shrink-0" />
                <span>L2 regularization</span>
              </li>
              <li className="flex items-start">
                <ChevronRight size={16} className="text-purple-500 mt-1 mr-1 flex-shrink-0" />
                <span>1000 max iterations</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

const FaultClassification = () => {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-2xl font-bold text-blue-800 mb-6">Fault Classification System</h2>
      
      <div className="grid grid-cols-3 gap-6">
        <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded shadow">
          <div className="flex items-center mb-3">
            <div className="bg-green-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-2">0</div>
            <h3 className="font-bold text-green-700">Not at Fault</h3>
          </div>
          <ul className="text-sm space-y-3">
            <li className="flex items-start">
              <AlertTriangle size={16} className="text-green-500 mt-1 mr-2 flex-shrink-0" />
              <span>Vehicle was stationary while other vehicle was moving</span>
            </li>
            <li className="flex items-start">
              <AlertTriangle size={16} className="text-green-500 mt-1 mr-2 flex-shrink-0" />
              <span>Vehicle was rear-ended while moving</span>
            </li>
            <li className="flex items-start">
              <AlertTriangle size={16} className="text-green-500 mt-1 mr-2 flex-shrink-0" />
              <span>Vehicle was following all traffic rules when another vehicle violated rules</span>
            </li>
            <li className="flex items-start">
              <AlertTriangle size={16} className="text-green-500 mt-1 mr-2 flex-shrink-0" />
              <span>Vehicle was properly stopped at traffic signal when hit</span>
            </li>
          </ul>
        </div>
        
        <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded shadow">
          <div className="flex items-center mb-3">
            <div className="bg-yellow-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-2">1</div>
            <h3 className="font-bold text-yellow-700">Partially at Fault</h3>
          </div>
          <ul className="text-sm space-y-3">
            <li className="flex items-start">
              <AlertTriangle size={16} className="text-yellow-500 mt-1 mr-2 flex-shrink-0" />
              <span>Both vehicles contributed to the accident</span>
            </li>
            <li className="flex items-start">
              <AlertTriangle size={16} className="text-yellow-500 mt-1 mr-2 flex-shrink-0" />
              <span>Weather/road conditions played significant role</span>
            </li>
            <li className="flex items-start">
              <AlertTriangle size={16} className="text-yellow-500 mt-1 mr-2 flex-shrink-0" />
              <span>Minor traffic violation that contributed to accident</span>
            </li>
            <li className="flex items-start">
              <AlertTriangle size={16} className="text-yellow-500 mt-1 mr-2 flex-shrink-0" />
              <span>Complex situations with shared responsibility (simultaneous lane changes)</span>
            </li>
          </ul>
        </div>
        
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded shadow">
          <div className="flex items-center mb-3">
            <div className="bg-red-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-2">2</div>
            <h3 className="font-bold text-red-700">Fully at Fault</h3>
          </div>
          <ul className="text-sm space-y-3">
            <li className="flex items-start">
              <AlertTriangle size={16} className="text-red-500 mt-1 mr-2 flex-shrink-0" />
              <span>Hit a stationary vehicle (front impact when other vehicle wasn't moving)</span>
            </li>
            <li className="flex items-start">
              <AlertTriangle size={16} className="text-red-500 mt-1 mr-2 flex-shrink-0" />
              <span>Rear-ended another vehicle</span>
            </li>
            <li className="flex items-start">
              <AlertTriangle size={16} className="text-red-500 mt-1 mr-2 flex-shrink-0" />
              <span>Violated clear traffic rules (ran red light, illegal turn)</span>
            </li>
            <li className="flex items-start">
              <AlertTriangle size={16} className="text-red-500 mt-1 mr-2 flex-shrink-0" />
              <span>Distracted, impaired, or negligent operation</span>
            </li>
          </ul>
        </div>
      </div>
      
      <div className="mt-6 p-4 bg-blue-50 rounded">
        <p className="text-sm text-blue-800">
          <strong>Implementation Note:</strong> The CrashML model applies these classification rules both for initial rule-based labeling and for machine learning prediction. The model learns to recognize patterns in the data that correlate with these fault categories.
        </p>
      </div>
    </div>
  );
};

const Presentation = () => {
  return (
    <div className="p-4 bg-gray-100 min-h-screen">
      <div className="grid grid-cols-1 gap-8">
        <TitleSlide />
        <ModelArchitecture />
        <FaultClassification />
      </div>
    </div>
  );
};

export default Presentation;
