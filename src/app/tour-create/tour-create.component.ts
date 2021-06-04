import { Component, OnInit } from '@angular/core';
import {TourDbService} from '../shared/tour-db.service';
import {Router, ActivatedRoute} from '@angular/router';
import {Tour} from '../shared/tour';

@Component({
  selector: 'tf-tour-create',
  templateUrl: './tour-create.component.html',
  styleUrls: ['./tour-create.component.css']
})
export class TourCreateComponent implements OnInit {

  constructor(
    private tdb: TourDbService,
    private route: ActivatedRoute,
    private router: Router
  ) { }

  ngOnInit(): void {
  }

  createTour(tour: Tour) {
    this.tdb.create(tour).subscribe( () => {
      this.router.navigate(['../..', 'tours'],
        {relativeTo: this.route});
    });
  }

}
