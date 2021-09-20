import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import reportWebVitals from './reportWebVitals';
import logo from './logo.svg';
import Axios from 'axios';
import './App.css';
import MakesDropdown from './MakesDropdown.js';
import YearDropdown from './YearDropdown.js';

// Component for automakers dropdown
function CarSearch() {
    const [years, setYears] = useState([]);
    const [models, setModels] = useState([]);
    const [yearProp, setYear] = useState("");
    const [makeSelection, setMakeSelection] = useState("");
    const yearsArray = [];

    useEffect(() => {
        // Update the document title using the browser API
        Axios.get("/api/v1/years").then((response) => {
            console.log(response.data.years);
            setYears(response.data.years);
        });

        Axios.post("/api/v1/models", {year: "2012", make: "NISSAN"}).then((response) => {
            console.log(response.data.models);
            setModels(response.data.models);
        });

    }, []);

    return (
        <div>
            <h2>YearSection:</h2>
            <form>
                <select name="years" id="years-dropdown">
                    <option value="" selected>Year</option>

                    {years.map((year, i) =>
                        <option value={years[i]}>{years[i]}</option>

                    )}
                </select>
                <select name="makes" id="makes">
                    <option value="" selected>Make</option>

                    {years.map((maker, i) =>
                        <option value={"bananas"}>PLACEHOLDER</option>

                    )}
                </select>
                <select name="models" id="models">
                    <option value="" selected>Model</option>

                    {models.map((maker, i) =>
                        <option value={models[i]}>{models[i]}</option>

                    )}
                </select>
                <button type="submit" id="search-button">CLick Here</button>
            </form>
        </div>
    );
}

export default CarSearch;