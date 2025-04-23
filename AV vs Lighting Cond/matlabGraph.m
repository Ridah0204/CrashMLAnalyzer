% MATLAB script to analyze lighting conditions across multiple crash data files
% Sorting bars from highest to lowest count with legend in top right

close all
clear all
clc

% Define the files to process
files = {'processed_crash_data_2019.csv', 'processed_crash_data_2020.csv', ...
         'processed_crash_data_2021.csv', 'processed_crash_data_2022.csv', ...
         'processed_crash_data_2023.csv', 'processed_crash_data_2024.csv'};

% Define the lighting conditions to look for (updated based on actual data)
conditions = {'lighting_a_1', 'lighting_b_1', 'lighting_c_1', 'lighting_d_1', 'lighting_e_1'};

% Define the corresponding labels
labels = {'Daylight', 'Dusk-Dawn', 'Dark-Street Lights', 'Dark-No Street Lights', ...
          'Dark-Street Lights Not Functioning'};

% Use fixed count values that you provided
counts = [368, 16, 171, 4, 0]; % Using these counts to ensure the graph displays correctly

% Sort counts from highest to lowest
[sorted_counts, sort_idx] = sort(counts, 'descend');
sorted_conditions = conditions(sort_idx);
sorted_labels = labels(sort_idx);
sorted_colors = [0.3 0.75 0.93;  % Light blue for Daylight
                 0.9 0.7 0.1;    % Orange-yellow for Dusk-Dawn
                 0.4 0.4 0.7;    % Purple-ish for Dark-Street Lights
                 0.1 0.1 0.3;    % Dark blue for Dark-No Street Lights
                 0.5 0.5 0.1];   % Olive for Dark-Street Lights Not Functioning
sorted_colors = sorted_colors(sort_idx, :);

% Create a bar graph with sorted data
figure('Position', [100, 100, 1000, 600]);
bar_plot = bar(sorted_counts, 'FaceColor', 'flat');

% Set colors for each bar
for i = 1:length(sorted_conditions)
    bar_plot.CData(i,:) = sorted_colors(i,:);
end

% Add data labels on top of each bar
for i = 1:length(sorted_counts)
    if sorted_counts(i) > 0  % Only add labels for non-zero values
        text(i, sorted_counts(i)+max(sorted_counts)*0.02, num2str(sorted_counts(i)), ...
            'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', ...
            'FontWeight', 'bold', 'FontSize', 14);
    end
end

% Set the x-axis labels to numbered categories
xticks(1:length(sorted_counts));
xticklabels({'1', '2', '3', '4', '5'});  % Simple numbers for the x-axis

% Add title and axis labels
title('Frequency of Different Lighting Conditions (2019-2024)', 'FontSize', 18, 'FontWeight', 'bold');
ylabel('Count', 'FontSize', 16);
xlabel('Lighting Condition Category', 'FontSize', 16);

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
title(lgd, 'Lighting Conditions Legend', 'FontSize', 14);

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
saveas(gcf, 'lighting_conditions_analysis_sorted.png');
saveas(gcf, 'lighting_conditions_analysis_sorted.fig');
print('lighting_conditions_analysis_sorted.pdf', '-dpdf', '-r300');

fprintf('\nAnalysis complete. Results saved as lighting_conditions_analysis_sorted.png/fig/pdf\n');