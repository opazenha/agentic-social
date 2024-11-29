from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import DallETool
import time
from datetime import datetime
import os
import re
import json

@CrewBase
class Social():
    """Social crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        super().__init__()
        print("\n=== Initializing Social class ===")
        try:
            self.dalle_tool = DallETool()
            print("DALL-E tool initialized successfully")
        except Exception as e:
            print(f"Error initializing DALL-E tool: {str(e)}")
            raise
            
        # Create images directory if it doesn't exist
        self.images_dir = os.path.join(os.path.dirname(__file__), 'generated_images')
        os.makedirs(self.images_dir, exist_ok=True)
        print(f"Images directory set up at: {self.images_dir}")
        self.markdown_filepath = None

    def generate_and_save_images(self, prompts: list) -> list:
        """Generate and save images for each prompt"""
        print("\n=== Starting image generation process ===")
        print(f"Received {len(prompts)} prompts to process")
        
        # Ensure requests is imported
        import requests
        from requests.exceptions import RequestException
        
        image_paths = []
        for i, prompt in enumerate(prompts, 1):
            try:
                print(f"\n--- Processing prompt {i}/{len(prompts)} ---")
                print(f"Prompt preview: {prompt[:200]}...")
                print("Calling DALL-E tool...")
                
                # Generate image using DALL-E
                response = self.dalle_tool.run(image_description=prompt)
                
                if not response:
                    print("Warning: No response received from DALL-E")
                    continue
                    
                print(f"DALL-E response received")
                
                # Parse response as JSON
                try:
                    response_data = json.loads(response)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON response: {str(e)}")
                    continue
                
                # Extract image URL from response
                image_url = response_data.get('image_url')
                if image_url:
                    print(f"Image URL received: {image_url}")
                    
                    try:
                        # Download image with timeout and verify=True for security
                        print("Downloading image from URL...")
                        image_response = requests.get(image_url, timeout=30, verify=True)
                        image_response.raise_for_status()  # Raise exception for bad status codes
                        
                        image_data = image_response.content
                        print(f"Downloaded image data size: {len(image_data)} bytes")
                        
                        if len(image_data) > 0:
                            # Save the image
                            image_path = self.save_image(image_data, i)
                            image_paths.append({
                                'path': image_path,
                                'url': image_url,
                                'size': len(image_data)
                            })
                            print(f"Successfully processed and saved image {i}")
                        else:
                            print("Error: Downloaded image data is empty")
                            
                    except RequestException as e:
                        print(f"Error downloading image: {str(e)}")
                        continue
                else:
                    print("Error: No image_url found in DALL-E response")
                    print(f"Response keys available: {response_data.keys()}")
                
                # Rate limiting
                if i < len(prompts):
                    print("Waiting 30 seconds before next generation...")
                    time.sleep(30)
                    print("Wait complete")
                
            except Exception as e:
                print(f"Error processing prompt {i}:")
                print(f"Error details: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
        
        print(f"\nImage generation complete. Generated {len(image_paths)} images")
        return image_paths

    def save_image(self, image_data: bytes, post_number: int) -> str:
        """Save the generated image with timestamp"""
        print(f"\n=== Saving image for post {post_number} ===")
        print(f"Image data size: {len(image_data)} bytes")
        
        # Ensure the directory exists
        os.makedirs(self.images_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'post_{post_number}_{timestamp}.png'
        filepath = os.path.join(self.images_dir, filename)
        print(f"Target filepath: {filepath}")
        
        try:
            # Write the image data
            with open(filepath, 'wb') as f:
                bytes_written = f.write(image_data)
            print(f"Wrote {bytes_written} bytes to file")
            
            # Verify the file was created and has content
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                if file_size > 0:
                    print(f"Successfully saved image. File size: {file_size} bytes")
                    return filepath
                else:
                    raise Exception(f"File was created but is empty (0 bytes)")
            else:
                raise Exception("File was not created")
                
        except Exception as e:
            print(f"Error saving image: {str(e)}")
            raise

    def save_posts_to_markdown(self, output: str, image_paths: list) -> str:
        """Save the prompts and image paths to a markdown file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"prompts_{timestamp}.md"
        
        # Create posts directory if it doesn't exist
        posts_dir = os.path.join(os.path.dirname(__file__), "generated_prompts")
        os.makedirs(posts_dir, exist_ok=True)
        
        filepath = os.path.join(posts_dir, filename)
        self.markdown_filepath = filepath  # Store the filepath
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write timestamp header
            f.write(f"# Social Media Prompts - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Write original output
            f.write("## Generated Content\n\n")
            f.write(output)
            f.write("\n\n")
            
            # Write image information
            f.write("## Generated Images\n\n")
            for i, image_info in enumerate(image_paths, 1):
                f.write(f"### Image {i}\n")
                f.write(f"- Path: {image_info['path']}\n")
                f.write(f"- Size: {image_info['size']} bytes\n")
                if 'url' in image_info:
                    f.write(f"- URL: {image_info['url']}\n")
                f.write("\n")
        
        return filepath

    def extract_prompts(self, output: str) -> list:
        """Extract prompts from the output"""
        import re
        # Use regex to find all prompts in the output
        prompt_pattern = r"--- PROMPT \d+:\s*(.*?)\n"
        prompts = re.findall(prompt_pattern, output, re.DOTALL)
        return prompts

    @before_kickoff
    def pull_data_example(self, inputs):
        print("\n=== Starting pull_data_example ===")
        if inputs is None:
            inputs = {}
        print("Initial inputs:", inputs)
        # Preserve existing inputs and add extra data
        inputs.update({
            'extra_data': "This is extra data"
        })
        print("Modified inputs:", inputs)
        return inputs

    def run(self, *, topic: str = 'faith and personal growth') -> dict:
        """Run the crew workflow"""
        try:
            # Create the crew first
            crew = self.crew()
            
            # Execute the crew tasks with initial inputs including topic
            initial_inputs = {'topic': topic}
            result = crew.kickoff(inputs=initial_inputs)
            
            # Log the results
            output = self.log_results(result)
            
            # Extract prompts from the output
            prompts = self.extract_prompts(str(result))
            if not prompts:
                raise ValueError("No prompts found in the output")
            
            # Generate and save images
            image_paths = self.generate_and_save_images(prompts)
            
            # Save posts to markdown
            markdown_filepath = self.save_posts_to_markdown(str(result), image_paths)
            print(f"Saved posts to markdown file: {markdown_filepath}")
            
            # Rename posts.md to task_posts_{timestamp}.md
            posts_dir = os.path.join(os.path.dirname(__file__), "generated_posts")
            old_file_path = os.path.join(posts_dir, "posts.md")
            if os.path.exists(old_file_path):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_file_path = os.path.join(posts_dir, f"task_posts_{timestamp}.md")
                os.rename(old_file_path, new_file_path)
                print(f"Renamed {old_file_path} to {new_file_path}")
            else:
                print("No posts.md file found to rename.")
            
            return str(result)
            
        except Exception as e:
            print(f"Error running crew: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise

    @agent
    def strategic_planner(self) -> Agent:
        print("\n=== Creating strategic planner agent ===")
        return Agent(
            config=self.agents_config['strategic_planner'],
            verbose=True
        )

    @agent
    def bible_expert(self) -> Agent:
        print("\n=== Creating bible expert agent ===")
        return Agent(
            config=self.agents_config['bible_expert'],
            verbose=True
        )

    @agent
    def researcher(self) -> Agent:
        print("\n=== Creating researcher agent ===")
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        print("\n=== Creating reporting analyst agent ===")
        return Agent(
            config=self.agents_config['reporting_analyst'],
            verbose=True
        )

    @agent
    def prompt_engineer(self) -> Agent:
        print("\n=== Creating prompt engineer agent ===")
        return Agent(
            config=self.agents_config['prompt_engineer'],
            verbose=True
        )

    @task
    def strategic_planning_task(self) -> Task:
        print("\n=== Creating strategic planning task ===")
        return Task(
            config=self.tasks_config['strategic_planning_task'],
        )

    @task
    def biblical_wisdom_task(self) -> Task:
        print("\n=== Creating biblical wisdom task ===")
        return Task(
            config=self.tasks_config['biblical_wisdom_task'],
        )

    @task
    def research_task(self) -> Task:
        print("\n=== Creating research task ===")
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def reporting_task(self) -> Task:
        """Create the reporting task"""
        print("\n=== Creating reporting task ===")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return Task(
            config=self.tasks_config['reporting_task'],
            output_file=f"generated_posts/task_posts_{timestamp}.md",
        )

    @task
    def image_generation_task(self) -> Task:
        print("\n=== Creating image generation task ===")
        return Task(
            config=self.tasks_config['image_generation_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Social crew"""
        print("\n=== Creating crew ===")
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

    @after_kickoff
    def log_results(self, output):
        """Process and format the output"""
        print("\n=== Starting log_results ===")
        print(f"Output type: {type(output)}")
        
        output_str = str(output)
        
        # Log the first part of the output for debugging
        print(f"Output preview: {output_str[:200]}...")
        
        return output_str
