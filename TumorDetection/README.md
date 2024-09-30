# Tumor Detection

This project is designed to use Matlab to train a simple classifier on brain MRI scans. By reading in images as matrices of grayscale values, eigenvectors are found by singular value decomposition. Using the eigenspace created, test images are classified based on their distance from the training images.

To run this project, use the TumorDetection.m file alongside the tumor_mri_images and normal_mri_images folder. Inside of the TumorDetection.m, set the image_name to the image you would like to classify and then run the file inside of Matlab. 
