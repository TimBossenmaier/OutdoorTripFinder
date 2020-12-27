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
    const params = this.route.snapshot.queryParamMap;
    const search = {
      long: params.get('long').toString(),
      lat: params.get('lat').toString(),
      dist: params.get('dist').toString()
    };
    this.tdb.getAllTours(search).subscribe(res => this.tours = res);
  }

}
