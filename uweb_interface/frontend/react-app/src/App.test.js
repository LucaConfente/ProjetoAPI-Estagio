import { render, screen } from '@testing-library/react';
import App from './App';

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});

// -----------------------------------------------------------------------

// Este arquivo contém um teste automatizado para o componente principal App do frontend React.
// Utiliza a Testing Library para renderizar o App e buscar um elemento de texto que contenha 'learn react'.
// O teste verifica se esse elemento está presente no DOM usando o matcher .toBeInTheDocument(),
// que é fornecido pela biblioteca @testing-library/jest-dom (importada automaticamente pelo setupTests.js).
// Esse teste é gerado por padrão pelo Create React App e serve como exemplo de como escrever testes de interface.

