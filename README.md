# DICOM Viewer

![Showcasing the app UI](README-Assets/app_ui.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)](https://pypi.org/project/PyQt5/)

## Table of Contents
- [Description](#description)
- [Features](#features)
- [How to Run It?](#how-to-run-it)
- [Toolstack](#toolstack)
- [Areas of Improvement](#areas-of-improvement)
- [Contributors](#contributors)
- [License](#license)


## Description

DICOM Viewer is a desktop application built using Python and PyQt, designed to streamline the viewing and analysis of medical images. It offers a wide array of features, ranging from basic viewing functionalities to advanced techniques like volume rendering, image processing, multiplanar reconstructions, annotations, and measurements. Also, it incorporates an AI model that functions as a Clinical Decision Support System (CDSS).

## Features

#### :white_check_mark: Basic Viewer Functionality
The app offers interactive viewer with tools for zoom, pan, contrast adjustment

#### :white_check_mark: Multiplanar Reconstruction (MPR):
You can view images in multiple planes (axial, sagittal, coronal).

#### :white_check_mark: Volume Rendering
3D representations of anatomical structures.

![Volume Rendering showcase](README-Assets/Volume_Renderer.png)

#### :white_check_mark: Image Adjustment and Enhancement
Features like windowing, sharpening, smoothing, and noise reduction.

#### :white_check_mark: Annotation and Measurement Tools:
The app offers tools for annotations with saving and loading notes capabilities, measurements (ruler and angle).

![Annotations_and_measurements showcase](README-Assets/Measurements_and_Annotations.png)

#### ✅ Comparison Mode of Different DICOM Images
Side-by-side viewing of different DICOM images for historical or multi-modality comparisons (e.g., CT vs. MRI).

#### ✅ AI Model that functions as a CDSS
Empower users by predicting potential medical interventions based on the current image, providing valuable insights to inform clinical decision-making.

## How to Run It?

To be able to use our app, you can simply follow these steps:
1. Install Python3 on your device. You can download it from <a href="https://www.python.org/downloads/">Here</a>.
2. Install the required packages by the following command.
```
pip install -r requirements.txt
```
3. Run the file with the name "main.py" located in the root.

> [!CAUTION]
> If you have Python 12+, the qDarkTheme package won't work. You must comment on out its import in the `main.py` and the line that calls it and sets up the theme.

## Contributors

Gratitude goes out to all team members for their valuable contributions to this project.

<div align="center">

| <a href="https://github.com/cln-Kafka"><img src="https://avatars.githubusercontent.com/u/100665578?v=4" width="100px" alt="@Kareem Noureddine"></a> | <a href="https://github.com/MuhammadSamiAhmad"><img src="https://avatars.githubusercontent.com/u/101589634?v=4" width="100px" alt="@M.Sami"></a> | <a href="https://github.com/hagersamir"><img src="https://avatars.githubusercontent.com/u/105936147?v=4" width="100px" alt="@hagersamir"></a> | <a href="https://github.com/mohandemadx"><img src="https://avatars.githubusercontent.com/u/102548631?v=4" width="100px" alt="@mohandemadx"></a> | <a href="https://github.com/JasmineTJ"><img src="https://avatars.githubusercontent.com/u/105980355?v=4" width="100px" alt="@JasmineTJ"></a> | <a href="https://github.com/Salma-me"><img src="https://avatars.githubusercontent.com/u/114951438?v=4" width="100px" alt="@Salma-me"></a> | <a href="https://github.com/Sarah2332"><img src="https://avatars.githubusercontent.com/u/103162590?v=4" width="100px" alt="@Sarah2332"></a> |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| [Kareem Noureddine](https://github.com/cln-Kafka) | [Mohamed Sami](https://github.com/MuhammadSamiAhmad) | [Hager Samir](https://github.com/hagersamir) | [Mohaned Emad](https://github.com/mohandemadx) | [Yassmeen Al-Jammal](https://github.com/JasmineTJ) | [Salma Ashraf](https://github.com/Salma-me) | [Sara Mohamed](https://github.com/Sarah2332) |

</div>

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.
