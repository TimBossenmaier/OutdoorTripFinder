import { Component, OnInit } from '@angular/core';
import {FormBuilder, FormGroup} from '@angular/forms';
import {TourDbService} from '../shared/tour-db.service';
import {ActivatedRoute, Router} from '@angular/router';

@Component({
  selector: 'tf-tour-search',
  templateUrl: './tour-search.component.html',
  styleUrls: ['./tour-search.component.css']
})
export class TourSearchComponent implements OnInit {

  coordinateForm: FormGroup;
  googleForm: FormGroup;
  coordinates: {long, lat};

  constructor(private fb: FormBuilder,
              private tdb: TourDbService,
              private route: ActivatedRoute,
              private router: Router) { }

  ngOnInit(): void {
    this.initForm();
  }

  private initForm() {
    if (this.coordinateForm) {return; }
    if (this.googleForm) {return; }

    this.coordinateForm = this.fb.group(
      {
        long: '',
        lat: '',
        dist: ''
      }
    );

    this.googleForm = this.fb.group(
      {
        dist: ''
      }
    );
  }

  submitForm(){
    const formValue = this.coordinateForm.value;
    const search = {
      long: formValue.long,
      lat: formValue.lat,
      dist: formValue.dist
    };
    this.coordinateForm.reset();
    this.router.navigate( ['../', 'tours'],
      {relativeTo: this.route, queryParams: {...search}});

  }

  search() {
    console.log('search');
    const formValue = this.googleForm.value;
    const search = {
      long: this.coordinates.long,
      lat: this.coordinates.lat,
      dist: formValue.dist
    };
    this.googleForm.reset();
    this.router.navigate(['../', 'tours'],
      {relativeTo: this.route, queryParams: {...search}});
  }

  searchLocation(coordinates: any) {
    this.coordinates = coordinates;
  }

}
