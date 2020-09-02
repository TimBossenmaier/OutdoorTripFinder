import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TourDbService } from '../shared/tour-db.service';
import {Tour } from '../shared/tour';

@Component({
  selector: 'tf-tour-details',
  templateUrl: './tour-details.component.html',
  styleUrls: ['./tour-details.component.css']
})
export class TourDetailsComponent implements OnInit {
tour: Tour;

  constructor(
    private tdb: TourDbService,
    private route: ActivatedRoute
  ) { }

  ngOnInit(): void {
    const params = this.route.snapshot.paramMap;
    this.tdb.getTourByID(params.get('id')).subscribe(t => this.tour = t);
  }

}
