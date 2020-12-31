import { Component, OnInit } from '@angular/core';
import {TourDbService} from '../shared/tour-db.service';

@Component({
  selector: 'tf-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  stats: {
    noTours: number,
    noCountry: number,
    noRegion: number,
    noLocation: number,
    popCountry: string,
    popRegion: string,
    popActivityType: string,
    popActivity: string
  };

  constructor(private tdb: TourDbService) { }

  ngOnInit(): void {
    this.tdb.getGeneralStats().subscribe(res => this.stats = res);
  }

}
