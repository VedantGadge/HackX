const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files (CSS, JS, images)
app.use('/static', express.static(path.join(__dirname, 'static')));

// Serve templates as static HTML
app.use('/templates', express.static(path.join(__dirname, 'templates')));

// Root route - serve index.html
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

// Other routes
app.get('/learn', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'learn_new.html'));
});

app.get('/classroom', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'classroom_home.html'));
});

app.get('/teacher', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'teacher.html'));
});

app.get('/student', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'student.html'));
});

// Start server
app.listen(PORT, () => {
    console.log('========================================');
    console.log('🎨 Frontend Server Started');
    console.log('========================================');
    console.log(`📍 Server running on: http://localhost:${PORT}`);
    console.log(`📁 Static files: http://localhost:${PORT}/static/`);
    console.log(`📄 Templates: http://localhost:${PORT}/templates/`);
    console.log('');
    console.log('Available routes:');
    console.log('  - http://localhost:' + PORT + '/');
    console.log('  - http://localhost:' + PORT + '/learn');
    console.log('  - http://localhost:' + PORT + '/classroom');
    console.log('  - http://localhost:' + PORT + '/teacher');
    console.log('  - http://localhost:' + PORT + '/student');
    console.log('');
    console.log('Press CTRL+C to stop');
    console.log('========================================');
});
