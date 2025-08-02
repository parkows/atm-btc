import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Container, Button } from '@mui/material';
import Dashboard from './pages/Dashboard';
import Simular from './pages/Simular';
import Detalhes from './pages/Detalhes';

function App() {
  return (
    <Router>
      <AppBar position="static">
        <Toolbar>
          <Button color="inherit" component={Link} to="/" sx={{ textTransform: 'none', fontSize: 22, fontWeight: 700, mr: 2 }}>
            ATM Cripto - Painel
          </Button>
          <Button color="inherit" component={Link} to="/">Dashboard</Button>
          <Button color="inherit" component={Link} to="/simular">Simular ATM</Button>
        </Toolbar>
      </AppBar>
      <Container sx={{ mt: 4 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/simular" element={<Simular />} />
          <Route path="/simular/:session_code" element={<Detalhes />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;
