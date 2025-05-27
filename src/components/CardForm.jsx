import React from 'react';

export default function CardForm() {
    return (
        <div className='card-form'>
            <form>
                <select name="team1" defaultValue="">
                    <option value="" disabled>Team 1</option>
                    <option value="teamA">Team A</option>
                    <option value="teamB">Team B</option>
                </select>
                <select name="team2" defaultValue="">
                    <option value="" disabled>Team 2</option>
                    <option value="teamA">Team A</option>
                    <option value="teamB">Team B</option>
                </select>
                <select name="venue" defaultValue="">
                    <option value="" disabled>Venue</option>
                    <option value="stadium1">Stadium 1</option>
                    <option value="stadium2">Stadium 2</option>
                </select>
            </form>

            <img 
              src="/seat-img.png" 
              alt="Seat Number" 
              style={{ width: '95%', display: 'block', margin: '0 auto' }} 
            />
        </div>
    );
}