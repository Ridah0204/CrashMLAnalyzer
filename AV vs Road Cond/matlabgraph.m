% MATLAB script to analyze road conditions across multiple crash data files
% Sorting bars from highest to lowest count with legend in top right
close all
clear all
clc

% Define the files to process
files = {'processed_crash_data_2019.csv', 'processed_crash_data_2020.csv', ...
'processed_crash_data_2021.csv', 'processed_crash_data_2022.csv', ...
'processed_crash_data_2023.csv', 'processed_crash_data_2024.csv'};

% Define the road conditions to look for
conditions = {'road_conditions_a_1', 'road_conditions_b_1', 'road_conditions_c_1', ...
'road_conditions_d_1', 'road_conditions_e_1', 'road_conditions_f_1', ...
'road_conditions_g_1', 'road_conditions_h_1', 'not_specified'};

% Define the corresponding labels
labels = {'Holes, Deep Rut', 'Loose Material on Roadway', 'Obstruction on Roadway', ...
'Construction-Repair Zone', 'Reduced Roadway Width', 'Flooded', ...
'Other', 'No Unusual Conditions', 'Not Specified'};

% Initialize counters for each road condition
road_counts = zeros(1, length(conditions));

% Process each CSV file to count road conditions
for file_idx = 1:length(files)
    % Read the current CSV file
    data = readtable(files{file_idx});
    
    % Extract the road_conditions column
    road_conditions = data.road_conditions;
    
    % Count each type of road condition
    for j = 1:length(road_conditions)
        condition = road_conditions{j};
        if isempty(condition) || any(ismissing(condition))
            road_counts(9) = road_counts(9) + 1; % Not specified
        elseif contains(condition, 'road_conditions_a_1')
            road_counts(1) = road_counts(1) + 1;
        elseif contains(condition, 'road_conditions_b_1')
            road_counts(2) = road_counts(2) + 1;
        elseif contains(condition, 'road_conditions_c_1')
            road_counts(3) = road_counts(3) + 1;
        elseif contains(condition, 'road_conditions_d_1')
            road_counts(4) = road_counts(4) + 1;
        elseif contains(condition, 'road_conditions_e_1')
            road_counts(5) = road_counts(5) + 1;
        elseif contains(condition, 'road_conditions_f_1')
            road_counts(6) = road_counts(6) + 1;
        elseif contains(condition, 'road_conditions_g_1')
            road_counts(7) = road_counts(7) + 1;
        elseif contains(condition, 'road_conditions_h_1')
            road_counts(8) = road_counts(8) + 1;
        else
            road_counts(9) = road_counts(9) + 1; % Not specified
        end
    end
end

% Sort counts from highest to lowest
[sorted_counts, sort_idx] = sort(road_counts, 'descend');
sorted_conditions = conditions(sort_idx);
sorted_labels = labels(sort_idx);

% Define distinct colors for each condition
colors = [
    0.8, 0.2, 0.2;  % Red - Holes, Deep Rut
    0.9, 0.6, 0.1;  % Orange - Loose Material
    0.2, 0.6, 0.8;  % Blue - Obstruction
    1.0, 0.8, 0.2;  % Yellow - Construction Zone
    0.6, 0.2, 0.6;  % Purple - Reduced Width
    0.1, 0.7, 0.9;  % Cyan - Flooded
    0.5, 0.5, 0.5;  % Gray - Other
    0.2, 0.7, 0.2;  % Green - No Unusual Conditions
    0.7, 0.7, 0.7;  % Light Gray - Not Specified
];
sorted_colors = colors(sort_idx, :);

% Create a bar graph with sorted data
figure('Position', [100, 100, 1000, 600]);
bar_plot = bar(sorted_counts, 'FaceColor', 'flat');

% Set colors for each bar
for i = 1:length(sorted_conditions)
    bar_plot.CData(i,:) = sorted_colors(i,:);
end

% Add data labels on top of each bar
for i = 1:length(sorted_counts)
    if sorted_counts(i) > 0 % Only add labels for non-zero values
        text(i, sorted_counts(i)+max(sorted_counts)*0.02, num2str(sorted_counts(i)), ...
            'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', ...
            'FontWeight', 'bold', 'FontSize', 14);
    end
end

% Set the x-axis labels to numbered categories
xticks(1:length(sorted_counts));
xticklabels({'1', '2', '3', '4', '5', '6', '7', '8', '9'}); % Simple numbers for the x-axis

% Add title and axis labels
title('Frequency of Road Conditions in Crash Data (2019-2024)', 'FontSize', 18, 'FontWeight', 'bold');
ylabel('Count', 'FontSize', 16);
xlabel('Road Condition Category', 'FontSize', 16);

% Create legend entries that match the sorted order of the bars
legend_entries = cell(length(sorted_counts), 1);
for i = 1:length(sorted_counts)
    legend_entries{i} = [num2str(i), ': ', sorted_labels{i}];
end

% Create invisible scatter points for the legend
hold on;
legend_handles = zeros(length(sorted_counts), 1);
for i = 1:length(sorted_counts)
    legend_handles(i) = scatter(NaN, NaN, 100, sorted_colors(i,:), 'filled', 's');
end

% Add the legend in the top right
lgd = legend(legend_handles, legend_entries, 'Location', 'northeast', 'FontSize', 12);
title(lgd, 'Road Conditions Legend', 'FontSize', 14);

% Add a text box with total data points analyzed
total_records = sum(sorted_counts);
file_info = sprintf('Total Files: %d\nTotal Records: %d', length(files), total_records);
annotation('textbox', [0.05, 0.02, 0.2, 0.08], 'String', file_info, ...
    'FitBoxToText', 'on', 'BackgroundColor', [0.95 0.95 0.95], ...
    'EdgeColor', [0.7 0.7 0.7], 'FontSize', 12);

% Adjust layout
grid on;
box on;
set(gca, 'FontSize', 14);

% Save the figure in multiple formats
saveas(gcf, 'road_conditions_analysis_sorted.png');
saveas(gcf, 'road_conditions_analysis_sorted.fig');
print('road_conditions_analysis_sorted.pdf', '-dpdf', '-r300');

fprintf('\nAnalysis complete. Results saved as road_conditions_analysis_sorted.png/fig/pdf\n');