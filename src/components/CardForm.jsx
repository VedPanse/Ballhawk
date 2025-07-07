import React, { useState } from 'react';
import '../App.css';

const teams = [
    "San Diego Padres", "Los Angeles Dodgers", "San Francisco Giants", "Arizona Diamondbacks", "Colorado Rockies",
    "Chicago Cubs", "St. Louis Cardinals", "Milwaukee Brewers", "Pittsburgh Pirates", "Cincinnati Reds",
    "Atlanta Braves", "New York Mets", "Philadelphia Phillies", "Miami Marlins", "Washington Nationals",
    "Houston Astros", "Texas Rangers", "Seattle Mariners", "Los Angeles Angels", "Oakland Athletics",
    "New York Yankees", "Boston Red Sox", "Toronto Blue Jays", "Baltimore Orioles", "Tampa Bay Rays",
    "Minnesota Twins", "Detroit Tigers", "Cleveland Guardians", "Kansas City Royals", "Chicago White Sox"
];

const stadiums = [
    "Petco Park", "Dodger Stadium", "Oracle Park", "Chase Field", "Coors Field",
    "Wrigley Field", "Busch Stadium", "American Family Field", "PNC Park", "Great American Ball Park",
    "Truist Park", "Citi Field", "Citizens Bank Park", "LoanDepot Park", "Nationals Park",
    "Minute Maid Park", "Globe Life Field", "T-Mobile Park", "Angel Stadium", "Oakland Coliseum",
    "Yankee Stadium", "Fenway Park", "Rogers Centre", "Camden Yards", "Tropicana Field",
    "Target Field", "Comerica Park", "Progressive Field", "Kauffman Stadium", "Guaranteed Rate Field",
    "Forbes Field" // legacy stadium used in demo
];

export default function CardForm() {
    const [team1, setTeam1] = useState('');
    const [team2, setTeam2] = useState('');
    const [venue, setVenue] = useState('');
    const [imageUrl, setImageUrl] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        setImageUrl(null);

        if (!team1 || !team2 || !venue) {
            setError("Please select all fields.");
            setLoading(false);
            return;
        }

        if (team1 === team2) {
            setError("Teams must be different.");
            setLoading(false);
            return;
        }

        const formData = new FormData();
        formData.append("team1", team1);
        formData.append("team2", team2);
        formData.append("venue", venue);

        try {
            const response = await fetch("http://localhost:8000/predict", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const msg = await response.text();
                throw new Error(msg || "Server error");
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            setImageUrl(url);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card-form">
            <form onSubmit={handleSubmit}>
                <select value={team1} onChange={(e) => setTeam1(e.target.value)}>
                    <option value="">Select Team 1</option>
                    {teams.map(t => (
                        <option key={t} value={t}>{t}</option>
                    ))}
                </select>

                <select value={team2} onChange={(e) => setTeam2(e.target.value)}>
                    <option value="">Select Team 2</option>
                    {teams.map(t => (
                        <option key={t} value={t}>{t}</option>
                    ))}
                </select>

                <select value={venue} onChange={(e) => setVenue(e.target.value)}>
                    <option value="">Select Stadium</option>
                    {stadiums.map(s => (
                        <option key={s} value={s}>{s}</option>
                    ))}
                </select>

                <button type="submit" disabled={loading} id='get-tickets'>
                    {loading ? "Predicting..." : "Get Best Seat Zone"}
                </button>
            </form>

            {error && <p style={{ color: 'red' }}>{error}</p>}

            {imageUrl && (
                <img
                    src={imageUrl}
                    alt="Best Seat Zone"
                    style={{ width: '95%', display: 'block', margin: '20px auto' }}
                />
            )}
        </div>
    );
}
