import "./App.css";
import { Route, Routes } from "react-router";
function App() {
  return (
    <Routes>
      <Route index element={<h1>home</h1>}></Route>
    </Routes>
  );
}

export default App;
