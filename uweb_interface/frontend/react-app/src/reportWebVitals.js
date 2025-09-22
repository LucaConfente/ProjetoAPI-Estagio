const reportWebVitals = onPerfEntry => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;

// --------------------------------------------------------------------------

// Este arquivo define a função reportWebVitals, utilizada para medir métricas de performance do frontend React (Web Vitals).
// Quando chamada com um callback (ex: reportWebVitals(console.log)), ela importa dinamicamente o pacote 'web-vitals'
// e executa as funções getCLS, getFID, getFCP, getLCP e getTTFB, que medem métricas como:
// - CLS (Cumulative Layout Shift): estabilidade visual
// - FID (First Input Delay): tempo até a primeira interação
// - FCP (First Contentful Paint): tempo até o primeiro conteúdo visível
// - LCP (Largest Contentful Paint): tempo até o maior conteúdo visível
// - TTFB (Time to First Byte): tempo até o primeiro byte da resposta
// O callback passado recebe os resultados dessas métricas. Se não for usado, nada acontece.
// Este arquivo é gerado pelo Create React App e serve apenas para monitoramento de performance do frontend, não afeta o funcionamento do app.
