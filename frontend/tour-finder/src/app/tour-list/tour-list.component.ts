import { Component, OnInit } from '@angular/core';
import { Tour } from '../shared/tour';
import { TourDbService } from '../shared/tour-db.service';
import {ActivatedRoute} from '@angular/router';
import {Observable} from 'rxjs';

@Component({
  selector: 'tf-tour-list',
  templateUrl: './tour-list.component.html',
  styleUrls: ['./tour-list.component.css']
})
export class TourListComponent implements OnInit {
  tours$: Observable<Tour[]>;

  constructor(private tdb: TourDbService,
              private route: ActivatedRoute) { }

  ngOnInit(): void {
    const params = this.route.snapshot.queryParams;
    if (params.long) {
      const search = {
        long: params.long.toString(),
        lat: params.lat.toString(),
        dist: params.dist.toString()
      };
      this. tours$ = this.tdb.getAllTours(search);
    } else if (params.country) {
      this.tours$ = this.tdb.getAllTours({country: params.country});
    } else if (params.region) {
      this.tours$ = this.tdb.getAllTours({region: params.region});
    } else {
      this.tours$ = this.tdb.getAllTours({country: '-1'});
    }
  }

}
