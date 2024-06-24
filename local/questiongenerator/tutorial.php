<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Import Questions to Moodle</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
        }
        .video {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>How to Import Questions to Moodle</h1>
        <div class="video">
            <video width="750" controls>
                <source src="path_to_your_video_tutorial.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <?php if (isset($_GET['xml'])): ?>
            <a href="<?php echo htmlspecialchars($_GET['xml']); ?>" download>Download Generated XML</a>
        <?php else: ?>
            <p>No XML file available for download.</p>
        <?php endif; ?>
    </div>
</body>
</html>
