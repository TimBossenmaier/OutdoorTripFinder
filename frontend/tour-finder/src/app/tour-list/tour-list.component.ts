import { Component, OnInit } from '@angular/core';
import { Tour } from '../shared/tour';
import { TourDbService } from '../shared/tour-db.service';
import {ActivatedRoute} from '@angular/router';

@Component({
  selector: 'tf-tour-list',
  templateUrl: './tour-list.component.html',
  styleUrls: ['./tour-list.component.css']
})
export class TourListComponent implements OnInit {
  tours: Tour[];

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
      this.tdb.getAllTours(search).subscribe(res => this.tours = res);
    } else if (params.country) {
      this.tdb.getAllTours({country: params.country}).subscribe(res => this.tours = res);
    } else if (params.region) {
      this.tdb.getAllTours({region: params.region}).subscribe(res => this.tours = res);
    } else {
      this.tdb.getAllTours({country: '-1'}).subscribe(res => this.tours = res);
    }
  }

}
