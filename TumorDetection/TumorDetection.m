[tumor_classifier, tumor_eigenvectors] = image_classification("tumor_mri_images/");
imagename = "tumor_mri.tif";
% imagename = "normal_mri.tif";
distance_tumor = classify_image(tumor_classifier, tumor_eigenvectors, imagename)
[normal_classifier, normal_eigenvectors] = image_classification("normal_mri_images/");
distance_normal = classify_image(normal_classifier, normal_eigenvectors, imagename)
if distance_tumor < distance_normal
    disp("This MRI scan contains a tumor.")
else
    disp("This MRI scan does not contain a tumor.")
end



function [classifier, eigenvectors] = image_classification(foldername)
    classifier_images = dir(fullfile(foldername, "*.tif"));
    k = 3;

    % Read in data matrix
    data_matrix = [];
    for i = 1:length(classifier_images)
        fullfile_name = foldername + classifier_images(i).name;
        [im, c_map] = imread(fullfile_name);
        im_matrix = im2double(im);

        % Convert image to grayscale
        if size(im_matrix, 3) ~= 1
            im_matrix = im_matrix(:, :, 2);
        end

        % Make im_matrix into column vector
        vector = im_matrix(:);
        data_matrix = [data_matrix, vector];

    end

    % Perform singular value decomposition
    [U, S, V] = svd(data_matrix, 'econ');
    
    % Find covariance matrix eigenvectors
    eigenvectors = U(:, 1:k);

    classifier = [];
    for i = 1:k
        vector = data_matrix(:, i);

        %Project image onto subspace of k eigenvectors
        point = [];
        for j = 1:k
            d = dot(eigenvectors(:, j),vector);
            point = vertcat(point, d);
        end
        classifier = [classifier, point];
    end
end


function [distance] = classify_image(classifier, eigenvectors, imagename)
    k = length(classifier);
    [im, c_map] = imread(imagename);
    im_matrix = im2double(im);
    vector = im_matrix(:);

    % Project image into subspace
    im_point = [];
    for i = 1:k
        d = dot(eigenvectors(:, i), vector);
        im_point = vertcat(im_point, d);
    end
    
    % Find distance to closest classifier point
    x_dist = im_point(1, 1) - classifier(1, 1);
    y_dist = im_point(2, 1) - classifier(2, 1);
    z_dist = im_point(3, 1) - classifier(3, 1);

    distance = sqrt(x_dist*x_dist + y_dist*y_dist + z_dist*z_dist);

    for i = 2:k
        x_dist = im_point(1, 1) - classifier(1, i);
        y_dist = im_point(2, 1) - classifier(2, i);
        z_dist = im_point(3, 1) - classifier(3, i);

        new_dist = sqrt(x_dist*x_dist + y_dist*y_dist + z_dist*z_dist);
        distance = min(distance, new_dist);
    end
end


