import { Component, OnInit } from '@angular/core';
import {TourDbService} from '../shared/tour-db.service';
import {AccountService} from '../shared/account.service';
import {User} from '../shared/user';

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

  user: User;

  constructor(private tdb: TourDbService,
              private as: AccountService) {
    this.user = this.as.userValue;
  }

  ngOnInit(): void {
    this.tdb.getGeneralStats().subscribe(res => this.stats = res);
  }

}
