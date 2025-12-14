// API Configuration
// To change the production API URL, edit PRODUCTION_API_URL below
const API_CONFIG = {
  // Production API base URL (update this if your API is deployed elsewhere)
  PRODUCTION_API_URL: "https://api.rcpch.ac.uk/clinical-calculators/v1",

  // Automatically detect local vs production environment
  baseUrl:
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
      ? "http://localhost:8000"
      : "https://api.rcpch.ac.uk/clinical-calculators/v1",

  endpoints: {
    calculators: "/list",
    calculate: "/calculate",
    calculatorDoc: (name) => `/${name}/doc`,
  },
};

export default API_CONFIG;
