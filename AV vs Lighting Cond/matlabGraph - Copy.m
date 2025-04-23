% MATLAB script to analyze lighting conditions across multiple crash data files
% Sorting bars from highest to lowest count

% Define the files to process
files = {'processed_crash_data_2019.csv', 'processed_crash_data_2020.csv', ...
         'processed_crash_data_2021.csv', 'processed_crash_data_2022.csv', ...
         'processed_crash_data_2023.csv', 'processed_crash_data_2024.csv'};

% Define the lighting conditions to look for (updated based on actual data)
conditions = {'lighting_a_1', 'lighting_b_1', 'lighting_c_1', 'lighting_d_1', 'lighting_e_1'};

% Define the corresponding labels
labels = {'Daylight', 'Dusk-Dawn', 'Dark-Street Lights', 'Dark-No Street Lights', ...
          'Dark-Street Lights Not Functioning'};

% Initialize a counter for each condition
counts = zeros(length(conditions), 1);

% Process each file
fprintf('Processing files:\n');
for i = 1:length(files)
    try
        % Read the current CSV file
        data = readtable(files{i});
        
        % Extract the lighting_conditions column
        lighting_conditions = data.lighting_conditions;
        
        % Count occurrences of each condition in this file
        for j = 1:length(conditions)
            % Use contains instead of strcmp to handle multiple values in one cell
            counts(j) = counts(j) + sum(contains(lighting_conditions, conditions{j}));
        end
        
        fprintf('Successfully processed file: %s\n', files{i});
    catch e
        fprintf('Error processing file %s: %s\n', files{i}, e.message);
    end
end

% Display the total counts
fprintf('\nCounts of lighting conditions across all files:\n');
for i = 1:length(conditions)
    fprintf('%s (%s): %d\n', labels{i}, conditions{i}, counts(i));
end

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
text_obj = text(1:length(sorted_counts), sorted_counts+max(sorted_counts)*0.02, ...
                num2str(sorted_counts), 'HorizontalAlignment', 'center', ...
                'VerticalAlignment', 'bottom', 'FontWeight', 'bold', 'FontSize', 14);

% Set the x-axis labels
xticks(1:length(sorted_counts));
xticklabels(sorted_labels);
xtickangle(45);  % Rotate labels for better visibility

% Add title and axis labels
title('Frequency of Different Lighting Conditions (2019-2024)', 'FontSize', 18, 'FontWeight', 'bold');
ylabel('Count', 'FontSize', 16);
xlabel('Lighting Conditions', 'FontSize', 16);

% Add a legend with the condition codes
legend_labels = cell(length(sorted_conditions), 1);
for i = 1:length(sorted_conditions)
    legend_labels{i} = [sorted_labels{i} ' (' sorted_conditions{i} ')'];
end
legend(legend_labels, 'Location', 'best', 'FontSize', 12);

% Add a text box with total data points analyzed
total_records = sum(sorted_counts);
file_info = sprintf('Total Files: %d\nTotal Records: %d', length(files), total_records);
annotation('textbox', [0.75, 0.02, 0.2, 0.08], 'String', file_info, ...
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