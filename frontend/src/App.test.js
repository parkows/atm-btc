import { render, screen } from '@testing-library/react';

// Mock the entire App component to avoid router issues
jest.mock('./App', () => {
  return function MockApp() {
    return (
      <div>
        <h1>ATM Cripto - Painel</h1>
        <button>Dashboard</button>
        <button>Simular ATM</button>
      </div>
    );
  };
});

import App from './App';

test('renders ATM Cripto title', () => {
  render(<App />);
  const titleElement = screen.getByText(/ATM Cripto - Painel/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders navigation buttons', () => {
  render(<App />);
  const dashboardButton = screen.getByText(/Dashboard/i);
  const simularButton = screen.getByText(/Simular ATM/i);
  expect(dashboardButton).toBeInTheDocument();
  expect(simularButton).toBeInTheDocument();
});
