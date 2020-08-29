import { Component, OnInit } from '@angular/core';
import { Tour } from '../shared/tour';
import { TourDbService } from '../shared/tour-db.service';

@Component({
  selector: 'tf-tour-list',
  templateUrl: './tour-list.component.html',
  styleUrls: ['./tour-list.component.css']
})
export class TourListComponent implements OnInit {
  tours: Tour[];

  constructor(private tdb: TourDbService) { }

  ngOnInit(): void {
    this.tours = this.tdb.getAllTours();
  }

}
