import { Injectable } from '@angular/core';

import { Tour } from './tour';

@Injectable({
  providedIn: 'root'
})
export class TourDbService {
tours: Tour[];

  constructor() {
    this.tours = [
      {
        id: '1',
        name: 'Zwei-Taeler-Steig',
        description: 'Auf dem Zwei-Täler-Steig im Naturpark Südschwarzwald lernen Wanderer zwei Gesichter der Region kennen.',
        activity_type: 'Wandern',
        source: 'Outdoor 04 2020',
        save_path: 'Europa\\Deutschland\\Zwei_Taeler_Steig.pdf',
        location: 'Waldkirch',
        region: 'Schwarwald',
        country: 'Deutschland',
        distance: 20.5
      },
      {
        id: '2',
        name: 'Karwendel',
        description: 'Stolze 125 Gipfel knacken im österreichisch-deutschen Karwendelgebirge die zweitausend-Meter-Marke - die meisten auf Tiroler Seite.',
        activity_type: 'Wandern',
        source: 'Outdoor 05 2020',
        save_path: 'Europa\\Oesterreich\\Karwendel.pdf',
        location: 'Rappenspitze',
        region: 'Tirol',
        country: 'Österreich',
        distance: 152.3
      }
    ];
  }

  getTourByID(id): Tour {
    return this.tours.find(tour => tour.id === id);
  }
}
