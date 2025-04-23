% MATLAB code to create a line graph from vehicle damage data 2019-2024

% Data from CSV analysis 
years = 2019:2024;

% Vehicle damage counts by category for each year
unk_counts = [19, 8, 15, 8, 20, 22];
none_counts = [14, 8, 6, 1, 10, 5];
minor_counts = [74, 27, 95, 47, 95, 77];
mod_counts = [0, 0, 0, 0, 0, 0];
major_counts = [1, 1, 1, 2, 6, 1];

% Create figure
figure('Position', [100, 100, 1000, 600]);

% Plot lines with markers
plot(years, unk_counts, 'o-', 'LineWidth', 2, 'DisplayName', 'UNK', 'MarkerFaceColor', 'auto');
hold on;
plot(years, none_counts, 's-', 'LineWidth', 2, 'DisplayName', 'NONE', 'MarkerFaceColor', 'auto');
plot(years, minor_counts, 'd-', 'LineWidth', 2, 'DisplayName', 'MINOR', 'MarkerFaceColor', 'auto');
plot(years, mod_counts, '^-', 'LineWidth', 2, 'DisplayName', 'MOD', 'MarkerFaceColor', 'auto');
plot(years, major_counts, 'p-', 'LineWidth', 2, 'DisplayName', 'MAJOR', 'MarkerFaceColor', 'auto');

% Add title and labels
title('Vehicle Damage Categories by Year (2019-2024)', 'FontSize', 16, 'FontWeight', 'bold');
xlabel('Year', 'FontSize', 14);
ylabel('Number of Incidents', 'FontSize', 14);

% Configure x-axis
xticks(years);
xticklabels(string(years));

% Add grid
grid on;

% Add legend
legend('Location', 'northwest', 'FontSize', 12);

% Add data labels
for i = 1:length(years)
    % Only add text for non-zero values (skipping MOD which is all zeros)
    text(years(i), unk_counts(i), num2str(unk_counts(i)), 'HorizontalAlignment', 'left', 'VerticalAlignment', 'bottom');
    text(years(i), none_counts(i), num2str(none_counts(i)), 'HorizontalAlignment', 'left', 'VerticalAlignment', 'bottom');
    text(years(i), minor_counts(i), num2str(minor_counts(i)), 'HorizontalAlignment', 'left', 'VerticalAlignment', 'bottom');
    text(years(i), major_counts(i), num2str(major_counts(i)), 'HorizontalAlignment', 'left', 'VerticalAlignment', 'bottom');
end

% Save figure (optional)
% saveas(gcf, 'vehicle_damage_by_year.png');
% saveas(gcf, 'vehicle_damage_by_year.fig');

% Add annotations
%dim = [0.15 0.65 0.3 0.3];
%str = {'Observations:', ...
       %'- MINOR damage is the most common category across all years', ...
       %'- MOD damage is consistently zero across all years', ...
       %'- MAJOR damage peaked in 2023'};
%annotation('textbox', dim, 'String', str, 'FitBoxToText', 'on', 'BackgroundColor', 'white', 'EdgeColor', 'black');