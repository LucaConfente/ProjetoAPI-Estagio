import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './assets/global.css';
import Layout from './components/Layout';
import Home from './pages/Home';
import Chat from './pages/Chat';
import Completions from './pages/Completions';

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/completions" element={<Completions />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
