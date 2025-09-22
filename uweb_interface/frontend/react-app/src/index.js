import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

reportWebVitals();

// ---------------------------------------------------------------------------

// Este arquivo é o ponto de entrada principal do frontend React.
// Ele importa os estilos globais, o componente App (aplicação principal) e a função reportWebVitals.
// Cria a raiz React no elemento 'root' do HTML e renderiza o App dentro do React.StrictMode (ajuda a identificar problemas).
// Por fim, chama reportWebVitals() para permitir monitoramento opcional de métricas de performance do frontend.
// Este arquivo é gerado pelo Create React App e é responsável por inicializar toda a aplicação React no navegador.
