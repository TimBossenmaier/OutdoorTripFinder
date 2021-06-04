import {Component, EventEmitter, OnInit, Output, } from '@angular/core';
import {Tour} from '../shared/tour';
import {FormArray, FormBuilder, FormControl, FormGroup, Validators} from '@angular/forms';
import {TourDbService} from '../shared/tour-db.service';
import {ActivityType} from '../shared/activity-type';
import {Location} from '../shared/location';

@Component({
  selector: 'tf-tour-form',
  templateUrl: './tour-form.component.html',
  styleUrls: ['./tour-form.component.css']
})
export class TourFormComponent implements OnInit {

  tourForm: FormGroup;
  activityTypes: ActivityType[];
  activityTypesNames: string[];
  locs: Location[];
  @Output() submitTour = new EventEmitter<Tour>();

  constructor(private fb: FormBuilder,
              private tdb: TourDbService) { }

  ngOnInit(): void {
    this.tdb.getActivityTypes().subscribe(res => this.activityTypes = res);
    this.activityTypesNames = this.activityTypes.map(at => at.name);
    this.tdb.getLocations().subscribe(res => this.locs = res);
    this.initForm();
  }


  private initForm() {
    if (this.tourForm) {return; }

    this.tourForm = this.fb.group(
      {
        name: ['', Validators.required],
        description: [''],
        activityType: new FormControl(),
        source: ['', Validators.required],
        savePath: ['', Validators.required],
        multiDay: ['', Validators.required],
        locations: this.buildLocationsArray([''])
      }
    );
  }

  get locations(): FormArray {
    return this.tourForm.get('locations') as FormArray;
  }

  private buildLocationsArray(values: string[]): FormArray {
    return this.fb.array(values, Validators.required);
  }

  addLocationControl() {
    this.locations.push(this.fb.control(''));
  }

  submitForm() {
   const formValue = this.tourForm.value;

   const locations = formValue.locations.filter(loc => loc);
   const activityType = this.activityTypes.find(a => a.name === formValue.activityType).id;

   const newTour: Tour = {
     ...formValue,
     activityType,
     locations
   };
   this.submitTour.emit(newTour);
   this.tourForm.reset();
  }

}
