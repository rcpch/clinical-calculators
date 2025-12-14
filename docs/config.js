// API Configuration
const API_CONFIG = {
  // Automatically detect local vs production environment
  baseUrl:
    window.location.hostname === "localhost"
      ? "http://localhost:8000"
      : "https://api.rcpch.ac.uk/clinical-calculators",
  endpoints: {
    calculators: "/list",
    calculate: "/calculate",
    calculatorDoc: (name) => `/${name}/doc`,
  },
};

export default API_CONFIG;
