% MATLAB code for accident data visualization
% Using pre-analyzed data to avoid CSV loading issues

% Define the data arrays (these values are from analysis of your CSVs)
midnight = [17, 21, 15, 26, 23, 17, 15]; % 12:00 am-03:59 am
morning = [51, 47, 69, 73, 51, 49, 39];  % 04:00 am-11:59 am
afternoon = [7, 5, 10, 5, 8, 6, 6];      % 12:00 pm-03:59 pm
evening = [0, 0, 0, 0, 0, 0, 0];         % 04:00 pm-07:59 pm
night = [0, 0, 0, 0, 0, 1, 0];           % 08:00 pm-11:59 pm

% Create the figure
figure('Position', [100, 100, 1200, 600]);

% Define days in the requested order
days = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'};
dayPositions = 1:7;

% Create the stacked bar graph (using only categories with significant data)
h = bar(dayPositions, [midnight; morning; afternoon]', 'stacked');

% Set custom colors similar to the sample graph
h(1).FaceColor = [0.2 0.5 0.8];  % Blue for midnight
h(2).FaceColor = [0.3 0.7 0.2];  % Green for morning
h(3).FaceColor = [0.9 0.5 0.1];  % Orange for afternoon

% Customize the appearance
title('Number of Accidents by Time of Day and Day of the Week', 'FontSize', 14, 'FontWeight', 'bold');
xlabel('Day of the Week', 'FontSize', 12);
ylabel('Number of Accidents', 'FontSize', 12);
set(gca, 'XTick', 1:7, 'XTickLabel', days);

% Add legend with time ranges
legendLabels = {
    'Midnight: 12:00 am-03:59 am', 
    'Morning: 04:00 am-11:59 am', 
    'Afternoon: 12:00 pm-03:59 pm'
};
legend(legendLabels, 'Location', 'northeast', 'FontSize', 10);

% Add grid and adjust properties
grid on;
box on;
set(gcf, 'Color', 'white');

% Adjust axes for better display
ylim([0 max(sum([midnight; morning; afternoon], 1))*1.1]);

% Add data labels
for i = 1:length(dayPositions)
    % Calculate positions for text
    midnight_pos = midnight(i)/2;
    morning_pos = midnight(i) + morning(i)/2;
    afternoon_pos = midnight(i) + morning(i) + afternoon(i)/2;
    
    % Add text labels
    text(i, midnight_pos, num2str(midnight(i)), 'HorizontalAlignment', 'center', 'Color', 'w', 'FontWeight', 'bold');
    text(i, morning_pos, num2str(morning(i)), 'HorizontalAlignment', 'center', 'Color', 'w', 'FontWeight', 'bold');
    text(i, afternoon_pos, num2str(afternoon(i)), 'HorizontalAlignment', 'center', 'Color', 'w', 'FontWeight', 'bold');
end

% Ensure proper spacing and layout
set(gca, 'FontSize', 11);
set(gca, 'TitleFontSizeMultiplier', 1.2);

% Save the figure if desired
% saveas(gcf, 'accident_analysis.png');