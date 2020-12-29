import { Component, OnInit } from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
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
  countryForm: FormGroup;
  coordinates: {long, lat};
  countries: {id, name, abbreviation} [];
  regions: {id, name} [];

  constructor(private fb: FormBuilder,
              private tdb: TourDbService,
              private route: ActivatedRoute,
              private router: Router) { }

  ngOnInit(): void {
    this.tdb.getCountries().subscribe(res => this.countries = res);
    this.initForm();
    $('#regionDropdown')
      .dropdown({
        onChange: function() {
          this.countryForm.patchValue({region: $('#regionDropdown').dropdown('get value')});
        }
          .bind(this)
      })
    ;
    $('#countryDropdown')
      .dropdown({
        onChange: function() {
          this.countryForm.patchValue({country: $('#countryDropdown').dropdown('get value')});
          this.tdb.getRegionByCountry(this.countryForm.value.country.toString()).subscribe(res => this.regions = res);
        }
        .bind(this)
      })
    ;
  }

  private initForm() {
    if (this.coordinateForm) {return; }
    if (this.googleForm) {return; }
    if (this.countryForm) {return; }

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

    this.countryForm = this.fb.group(
      {
        country: ['', Validators.required],
        region:  ['']
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

  country() {
    const formValue = this.countryForm.value;
    console.log(formValue.country, formValue.region);
  }

  searchLocation(coordinates: any) {
    this.coordinates = coordinates;
  }

}
