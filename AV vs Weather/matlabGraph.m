% MATLAB script to analyze weather conditions across multiple crash data files
% Sorting bars from highest to lowest count with legend in top right
close all
clear all
clc

% Define the files to process
files = {'processed_crash_data_2019.csv', 'processed_crash_data_2020.csv', ...
'processed_crash_data_2021.csv', 'processed_crash_data_2022.csv', ...
'processed_crash_data_2023.csv', 'processed_crash_data_2024.csv', ...
};

% Define the weather conditions to look for
conditions = {'weather_a_1', 'weather_b_1', 'weather_c_1', ...
'weather_d_1', 'weather_e_1', 'weather_f_1', ...
'weather_g_1', 'not_specified'};

% Define the corresponding labels
labels = {'Clear', 'Cloudy', 'Raining', ...
'Snowing', 'Fog/Visibility', 'Other', ...
'Wind', 'Not Specified'};

% Initialize counters for each weather condition
weather_counts = zeros(1, length(conditions));

% Process each CSV file to count weather conditions
for file_idx = 1:length(files)
    % Read the current CSV file
    data = readtable(files{file_idx});
    
    % Extract the weather_conditions column
    weather_conditions = data.weather_conditions;
    
    % Count each type of weather condition
    for j = 1:length(weather_conditions)
        condition = weather_conditions{j};
        if isempty(condition) || any(ismissing(condition))
            weather_counts(8) = weather_counts(8) + 1; % Not specified
        elseif contains(condition, 'weather_a_1')
            weather_counts(1) = weather_counts(1) + 1;
        elseif contains(condition, 'weather_b_1')
            weather_counts(2) = weather_counts(2) + 1;
        elseif contains(condition, 'weather_c_1')
            weather_counts(3) = weather_counts(3) + 1;
        elseif contains(condition, 'weather_d_1')
            weather_counts(4) = weather_counts(4) + 1;
        elseif contains(condition, 'weather_e_1')
            weather_counts(5) = weather_counts(5) + 1;
        elseif contains(condition, 'weather_f_1')
            weather_counts(6) = weather_counts(6) + 1;
        elseif contains(condition, 'weather_g_1')
            weather_counts(7) = weather_counts(7) + 1;
        else
            weather_counts(8) = weather_counts(8) + 1; % Not specified
        end
    end
end

% Sort counts from highest to lowest
[sorted_counts, sort_idx] = sort(weather_counts, 'descend');
sorted_conditions = conditions(sort_idx);
sorted_labels = labels(sort_idx);

% Define distinct colors for each condition
colors = [
    0.3, 0.8, 1.0;  % Light blue - Clear
    0.7, 0.7, 0.7;  % Gray - Cloudy
    0.2, 0.2, 0.8;  % Dark blue - Raining
    0.9, 0.9, 1.0;  % Very light blue - Snowing
    0.8, 0.8, 0.8;  % Light gray - Fog/Visibility
    1.0, 0.7, 0.3;  % Orange - Other
    0.4, 0.9, 0.4;  % Green - Wind
    0.5, 0.5, 0.5;  % Medium gray - Not Specified
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
xticklabels({'1', '2', '3', '4', '5', '6', '7', '8'}); % Simple numbers for the x-axis

% Add title and axis labels
title('Frequency of Weather Conditions in Crash Data (2019-2024)', 'FontSize', 18, 'FontWeight', 'bold');
ylabel('Count', 'FontSize', 16);
xlabel('Weather Condition Category', 'FontSize', 16);

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
title(lgd, 'Weather Conditions Legend', 'FontSize', 14);

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
saveas(gcf, 'weather_conditions_analysis_sorted.png');
saveas(gcf, 'weather_conditions_analysis_sorted.fig');
print('weather_conditions_analysis_sorted.pdf', '-dpdf', '-r300');

fprintf('\nAnalysis complete. Results saved as weather_conditions_analysis_sorted.png/fig/pdf\n');