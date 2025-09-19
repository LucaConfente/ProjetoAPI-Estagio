//  principal de layout
import React from 'react';

const Layout = ({ children }) => (
  <div className="layout">
    {/* Header, Sidebar, Footer... */}
    {children}
  </div>
);

export default Layout;
