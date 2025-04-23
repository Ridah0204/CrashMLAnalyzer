% MATLAB code to analyze impact points in crash data from 2019-2024
% This code counts occurrences of front, rear, driver_side, and passenger_side
% in the impact_points column and creates a bar graph

% Initialize arrays to store counts
years = 2019:2024;
num_years = length(years);
front_counts = zeros(1, num_years);
rear_counts = zeros(1, num_years);
driver_side_counts = zeros(1, num_years);
passenger_side_counts = zeros(1, num_years);

% Process each CSV file
for i = 1:num_years
    % Construct filename
    filename = sprintf('processed_crash_data_%d.csv', years(i));
    
    % Read the CSV file
    data = readtable(filename);
    
    % Get the impact_points column
    impact_points = data.impact_points;
    
    % Count occurrences of each impact point type
    % Using contains function to find substrings within the impact_points field
    front_counts(i) = sum(contains(impact_points, 'front', 'IgnoreCase', true));
    rear_counts(i) = sum(contains(impact_points, 'rear', 'IgnoreCase', true));
    driver_side_counts(i) = sum(contains(impact_points, 'driver_side', 'IgnoreCase', true));
    passenger_side_counts(i) = sum(contains(impact_points, 'passenger_side', 'IgnoreCase', true));
    
    % Print results for each year
    fprintf('Year %d:\n', years(i));
    fprintf('  Front: %d\n', front_counts(i));
    fprintf('  Rear: %d\n', rear_counts(i));
    fprintf('  Driver Side: %d\n', driver_side_counts(i));
    fprintf('  Passenger Side: %d\n', passenger_side_counts(i));
end

% Create a grouped bar chart
figure('Position', [100, 100, 1000, 600]);
bar_data = [front_counts; rear_counts; driver_side_counts; passenger_side_counts]';
bar_handle = bar(years, bar_data);

% Set colors for bars
set(bar_handle(1), 'FaceColor', [0.2, 0.6, 1.0]);   % Blue for front
set(bar_handle(2), 'FaceColor', [1.0, 0.4, 0.4]);   % Red for rear
set(bar_handle(3), 'FaceColor', [0.4, 0.8, 0.4]);   % Green for driver side
set(bar_handle(4), 'FaceColor', [0.8, 0.6, 0.2]);   % Gold for passenger side

% Add labels, title, and legend
xlabel('Year', 'FontSize', 12, 'FontWeight', 'bold');
ylabel('Number of Occurrences', 'FontSize', 12, 'FontWeight', 'bold');
title('Impact Points in Crashes (2019-2024)', 'FontSize', 14, 'FontWeight', 'bold');
legend('Front', 'Rear', 'Driver Side', 'Passenger Side', 'Location', 'best');
grid on;

% Customize grid
grid minor;
box on;

% Get bar positions
[ngroups, nbars] = size(bar_data);
% Get the x coordinate of the bars
x = nan(nbars, ngroups);
for i = 1:nbars
    x(i,:) = bar_handle(i).XEndPoints;
end

% Add data labels directly above each bar with consistent formatting
for i = 1:ngroups  % For each year
    for j = 1:nbars  % For each impact type (Front, Rear, Driver Side, Passenger Side)
        % Only add label if the count is greater than 0
        if bar_data(i,j) > 0
            text(x(j,i), bar_data(i,j) + 1.5, num2str(bar_data(i,j)), ...
                'HorizontalAlignment', 'center', ...
                'VerticalAlignment', 'bottom', ...
                'FontWeight', 'bold', ...
                'FontSize', 10, ...
                'BackgroundColor', [1 1 1 0.7], ... % Semi-transparent white background
                'Margin', 2);                        % Add small margin around text
        end
    end
end

% Save the figure
saveas(gcf, 'impact_points_analysis.png');
fprintf('Analysis complete. Figure saved as "impact_points_analysis.png"\n');