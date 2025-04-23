% MATLAB Script to analyze autonomous_mode data from multiple CSV files
% and create bar graph and pie chart visualizations

% Clear workspace and command window
clear all;
clc;

% Define the CSV files to process
csv_files = {
    'processed_crash_data_2019.csv'
    'processed_crash_data_2020.csv'
    'processed_crash_data_2021.csv'
    'processed_crash_data_2022.csv'
    'processed_crash_data_2023.csv'
    'processed_crash_data_2024.csv'
};

% Initialize arrays to store results
years = 2019:2024;
yes_counts = zeros(1, length(csv_files));
no_counts = zeros(1, length(csv_files));
total_counts = zeros(1, length(csv_files));

% Process each CSV file
for i = 1:length(csv_files)
    % Read the CSV file
    data = readtable(csv_files{i});
    
    % Count occurrences of "Yes" and "No" in autonomous_mode column
    yes_counts(i) = sum(strcmp(data.autonomous_mode, 'Yes'));
    no_counts(i) = sum(strcmp(data.autonomous_mode, 'No'));
    total_counts(i) = height(data);
    
    % Print results for each file
    fprintf('File: %s\n', csv_files{i});
    fprintf('  Total records: %d\n', total_counts(i));
    fprintf('  Autonomous mode "Yes": %d (%.1f%%)\n', yes_counts(i), 100*yes_counts(i)/total_counts(i));
    fprintf('  Autonomous mode "No": %d (%.1f%%)\n', no_counts(i), 100*no_counts(i)/total_counts(i));
    fprintf('\n');
end

% Calculate overall totals
total_yes = sum(yes_counts);
total_no = sum(no_counts);
grand_total = sum(total_counts);

fprintf('Overall Results:\n');
fprintf('  Total records: %d\n', grand_total);
fprintf('  Autonomous mode "Yes": %d (%.1f%%)\n', total_yes, 100*total_yes/grand_total);
fprintf('  Autonomous mode "No": %d (%.1f%%)\n', total_no, 100*total_no/grand_total);

% Create figure for visualizations
figure('Position', [100, 100, 1200, 600]);

% 1. Bar Graph by Year
subplot(2, 2, 1);
bar(years, [yes_counts; no_counts]', 'stacked');
title('Autonomous Mode Usage by Year');
xlabel('Year');
ylabel('Number of Incidents');
legend('Autonomous Mode: Yes', 'Autonomous Mode: No');
grid on;

% 2. Percentage Bar Graph
subplot(2, 2, 2);
percentages = [yes_counts./total_counts*100; no_counts./total_counts*100]';
bar(years, percentages, 'stacked');
title('Autonomous Mode Usage (%) by Year');
xlabel('Year');
ylabel('Percentage (%)');
legend('Autonomous Mode: Yes', 'Autonomous Mode: No');
ylim([0 100]);
grid on;

% 3. Overall Pie Chart
subplot(2, 2, 3);
pie([total_yes, total_no], {'Autonomous: Yes', 'Autonomous: No'});
title('Overall Autonomous Mode Usage (2019-2024)');

% 4. Multiple Pie Charts for Each Year
subplot(2, 2, 4);
pie3([total_yes, total_no]);
explode = [1 0];
title('3D Pie Chart of Overall Autonomous Mode Usage');
legend({'Autonomous: Yes', 'Autonomous: No'}, 'Location', 'southoutside');

% Create a new figure for individual pie charts by year
figure('Position', [100, 100, 1200, 400]);
for i = 1:length(years)
    subplot(1, 6, i);
    pie([yes_counts(i), no_counts(i)]);
    title(sprintf('%d', years(i)));
    if i == 1
        legend({'Yes', 'No'}, 'Location', 'southoutside');
    end
end
sgtitle('Autonomous Mode Usage by Year');

% Save figures
saveas(gcf, 'autonomous_mode_analysis_pies.png');