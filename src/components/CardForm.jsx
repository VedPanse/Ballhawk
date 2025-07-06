import React, { useState } from 'react';

const teams = [
  "Arizona Diamondbacks", "Atlanta Braves", "Baltimore Orioles", "Boston Red Sox", "Chicago White Sox",
  "Chicago Cubs", "Cincinnati Reds", "Cleveland Guardians", "Colorado Rockies", "Detroit Tigers",
  "Houston Astros", "Kansas City Royals", "Los Angeles Angels", "Los Angeles Dodgers", "Miami Marlins",
  "Milwaukee Brewers", "Minnesota Twins", "New York Yankees", "New York Mets", "Oakland Athletics",
  "Philadelphia Phillies", "Pittsburgh Pirates", "San Diego Padres", "San Francisco Giants",
  "Seattle Mariners", "St. Louis Cardinals", "Tampa Bay Rays", "Texas Rangers", "Toronto Blue Jays", "Washington Nationals"
];

const stadiums = [
  "Angel Stadium", "Minute Maid Park", "Oakland Coliseum", "Rogers Centre",
  "Truist Park", "American Family Field", "Busch Stadium", "Wrigley Field",
  "Chase Field", "Dodger Stadium", "Oracle Park", "Progressive Field",
  "T-Mobile Park", "loanDepot Park", "Citi Field", "Nationals Park",
  "Camden Yards", "Petco Park", "Citizens Bank Park", "PNC Park",
  "Globe Life Field", "Tropicana Field", "Fenway Park", "Great American Ball Park",
  "Coors Field", "Kauffman Stadium", "Comerica Park", "Target Field",
  "Guaranteed Rate Field", "Yankee Stadium"
];

export default function CardForm() {
  const [team1, setTeam1] = useState('');
  const [team2, setTeam2] = useState('');
  const [venue, setVenue] = useState('');

  const teamConflict = team1 && team2 && team1 === team2;

  return (
    <div className='card-form'>
      <form>
        <select name="team1" value={team1} onChange={(e) => setTeam1(e.target.value)}>
          <option value="" disabled>Team 1</option>
          {teams.map((team) => (
            <option key={team} value={team}>{team}</option>
          ))}
        </select>

        <select name="team2" value={team2} onChange={(e) => setTeam2(e.target.value)}>
          <option value="" disabled>Team 2</option>
          {teams.map((team) => (
            <option key={team} value={team}>{team}</option>
          ))}
        </select>

        <select name="venue" value={venue} onChange={(e) => setVenue(e.target.value)}>
          <option value="" disabled>Venue</option>
          {stadiums.map((stadium) => (
            <option key={stadium} value={stadium}>{stadium}</option>
          ))}
        </select>

        {teamConflict && (
          <p style={{ color: 'red', fontWeight: 'bold' }}>
            ⚠️ Team 1 and Team 2 must be different!
          </p>
        )}
      </form>

      <img 
        src="/seat-img.png" 
        alt="Seat Number" 
        style={{ width: '95%', display: 'block', margin: '0 auto' }} 
      />
    </div>
  );
}
